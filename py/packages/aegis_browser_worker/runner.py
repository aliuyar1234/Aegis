from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from .artifacts import BrowserArtifactStore
from .errors import BrowserVerificationError, UnsupportedWorkflowError
from .models import (
    ArtifactRecord,
    BrowserHandleState,
    BrowserObservation,
    BrowserWorkflowResult,
    MUTATING_STEP_KINDS,
    READ_ONLY_STEP_KINDS,
    WorkerExecutionContext,
)
from .protocols import BrowserAutomationBackend
from .recovery import BrowserRecoverySerializer


class BrowserWorkflowRunner:
    """Executes the browser wedge across read-only and Phase 08 effectful fixtures."""

    _MUTATING_TOOLS = {"browser.submit", "browser.click", "browser.delete"}

    def __init__(
        self,
        backend: BrowserAutomationBackend,
        *,
        artifact_store: BrowserArtifactStore | None = None,
        recovery_serializer: BrowserRecoverySerializer | None = None,
    ) -> None:
        self._backend = backend
        self._artifact_store = artifact_store or BrowserArtifactStore()
        self._recovery_serializer = recovery_serializer or BrowserRecoverySerializer()

    async def run_fixture(
        self,
        fixture: dict[str, Any],
        *,
        context: WorkerExecutionContext | None = None,
        dispatch: dict[str, Any] | None = None,
    ) -> BrowserWorkflowResult:
        context = context or WorkerExecutionContext(worker_id="browser-worker-local")
        dispatch = dispatch or {}
        self._validate_fixture(fixture)

        if fixture.get("expected_policy_decision") == "deny":
            return self._build_rejected_result(fixture, context)

        mutation_class = fixture.get("mutation_class")
        read_only = mutation_class == "read_only"
        if not read_only:
            self._validate_effectful_dispatch(fixture, context, dispatch)

        session = await self._backend.open_session(read_only=read_only)
        page = await session.new_page()
        observations: list[BrowserObservation] = []
        artifact_kinds: list[str] = []
        artifacts: list[ArtifactRecord] = []
        created_at = datetime.now(UTC).isoformat()
        mutation_started = False
        uncertainty_triggered = False

        handle = BrowserHandleState(
            browser_handle_id=f"browser-handle-{uuid4().hex}",
            provider_kind="playwright",
            provider_session_ref=session.session_ref,
            page_ref=session.page_ref,
            state_ref=f"fixture:{fixture['id']}",
            last_observed_at=created_at,
            restart_hint=f"reattach:{fixture['id']}",
        )

        try:
            for index, step in enumerate(fixture["steps"], start=1):
                kind = step["kind"]
                if kind in MUTATING_STEP_KINDS and not mutation_started:
                    mutation_started = True
                    observations.extend(
                        await self._capture_named_artifacts(
                            context=context,
                            created_at=created_at,
                            fixture=fixture,
                            artifacts=artifacts,
                            handle=handle,
                            artifact_kinds=artifact_kinds,
                            page=page,
                            kinds=["pre_write_screenshot"],
                            start_index=len(observations) + 1,
                        )
                    )

                observation = await self._run_step(
                    context=context,
                    created_at=created_at,
                    fixture=fixture,
                    artifacts=artifacts,
                    handle=handle,
                    observations=observations,
                    page=page,
                    step=step,
                    index=index + len(observations),
                )
                observations.append(observation)
                if observation.artifact_kind is not None:
                    artifact_kinds.append(observation.artifact_kind)

                if kind in MUTATING_STEP_KINDS:
                    observations.extend(
                        await self._capture_named_artifacts(
                            context=context,
                            created_at=created_at,
                            fixture=fixture,
                            artifacts=artifacts,
                            handle=handle,
                            artifact_kinds=artifact_kinds,
                            page=page,
                            kinds=["post_write_screenshot"],
                            start_index=len(observations) + 1,
                        )
                    )

                    if self._uncertainty_triggered(fixture):
                        uncertainty_triggered = True
                        break

            observations.extend(
                await self._capture_expected_artifacts(
                    context=context,
                    created_at=created_at,
                    fixture=fixture,
                    artifacts=artifacts,
                    handle=handle,
                    page=page,
                    artifact_kinds=artifact_kinds,
                    start_index=len(observations) + 1,
                )
            )

            handle.page_ref = session.page_ref
            handle.current_url = page.url
            handle.read_only_baseline_complete = True
            recovery = self._recovery_serializer.build_recovery_point(
                handle=handle,
                artifact_ids=[artifact.artifact_id for artifact in artifacts],
                fixture_id=fixture["id"],
            )

            trace_artifact_id = self._artifact_id_for_kind(artifacts, "trace")

            if read_only:
                return BrowserWorkflowResult(
                    fixture_id=fixture["id"],
                    status="completed",
                    handle=handle,
                    observations=observations,
                    artifact_kinds=artifact_kinds,
                    artifacts=artifacts,
                    recovery=recovery,
                    final_url=page.url,
                    policy_decision=fixture.get("expected_policy_decision"),
                )

            status = "uncertain" if uncertainty_triggered else "submitted"
            return BrowserWorkflowResult(
                fixture_id=fixture["id"],
                status=status,
                handle=handle,
                observations=observations,
                artifact_kinds=artifact_kinds,
                artifacts=artifacts,
                recovery=recovery,
                final_url=page.url,
                policy_decision=fixture.get("expected_policy_decision"),
                uncertain_side_effect=uncertainty_triggered,
                uncertainty_trigger=fixture.get("uncertainty_trigger") if uncertainty_triggered else None,
                requires_operator_takeover=bool(
                    uncertainty_triggered and fixture.get("requires_operator_takeover_on_uncertainty")
                ),
                trace_artifact_id=trace_artifact_id,
                submit_result=self._submit_result(
                    status=status,
                    artifacts=artifacts,
                    trace_artifact_id=trace_artifact_id,
                    fixture=fixture,
                ),
            )
        finally:
            await page.close()
            await session.close()

    def _build_rejected_result(
        self,
        fixture: dict[str, Any],
        context: WorkerExecutionContext,
    ) -> BrowserWorkflowResult:
        created_at = datetime.now(UTC).isoformat()
        handle = BrowserHandleState(
            browser_handle_id=f"browser-handle-{uuid4().hex}",
            provider_kind="playwright",
            state_ref=f"fixture:{fixture['id']}",
            last_observed_at=created_at,
            restart_hint=f"reattach:{fixture['id']}",
        )
        recovery = self._recovery_serializer.build_recovery_point(
            handle=handle,
            artifact_ids=[],
            fixture_id=fixture["id"],
        )
        return BrowserWorkflowResult(
            fixture_id=fixture["id"],
            status="rejected",
            handle=handle,
            observations=[
                BrowserObservation(
                    step_kind="policy_rejected",
                    detail="policy denied effectful browser mutation",
                    data={
                        "tool_id": fixture.get("tool_id"),
                        "worker_id": context.worker_id,
                    },
                )
            ],
            artifact_kinds=[],
            artifacts=[],
            recovery=recovery,
            final_url=None,
            policy_decision=fixture.get("expected_policy_decision"),
            submit_result=self._submit_result(
                status="rejected",
                artifacts=[],
                trace_artifact_id=None,
                fixture=fixture,
            ),
        )

    def _validate_fixture(self, fixture: dict[str, Any]) -> None:
        mutation_class = fixture.get("mutation_class")

        if mutation_class == "read_only":
            if fixture.get("requires_approval"):
                raise UnsupportedWorkflowError("Read-only fixtures cannot require approval.")

            for step in fixture.get("steps", []):
                kind = step["kind"]
                if kind in MUTATING_STEP_KINDS:
                    raise UnsupportedWorkflowError(
                        f"Read-only browser worker rejects mutating step kind {kind!r}."
                    )
                if kind not in READ_ONLY_STEP_KINDS:
                    raise UnsupportedWorkflowError(
                        f"Browser worker does not recognize step kind {kind!r}."
                    )
            return

        tool_id = fixture.get("tool_id")
        if tool_id not in self._MUTATING_TOOLS:
            raise UnsupportedWorkflowError(
                f"Effectful browser fixture must use a mutating tool id, got {tool_id!r}."
            )

        for step in fixture.get("steps", []):
            kind = step["kind"]
            if kind not in READ_ONLY_STEP_KINDS and kind not in MUTATING_STEP_KINDS:
                raise UnsupportedWorkflowError(
                    f"Browser worker does not recognize step kind {kind!r}."
                )
            if kind == "fill" and "value" not in step:
                raise UnsupportedWorkflowError("Fill steps must declare a value in effectful fixtures.")

        if fixture.get("expected_policy_decision") == "require_approval":
            expected_artifacts = set(fixture.get("expected_artifacts", []))
            required = {"pre_write_screenshot", "post_write_screenshot", "dom_snapshot", "trace"}
            if not required.issubset(expected_artifacts):
                raise UnsupportedWorkflowError(
                    "Effectful approval-bound fixtures must declare pre/post screenshot, dom snapshot, and trace artifacts."
                )

    def _validate_effectful_dispatch(
        self,
        fixture: dict[str, Any],
        context: WorkerExecutionContext,
        dispatch: dict[str, Any],
    ) -> None:
        if fixture.get("requires_approval") and dispatch.get("approval_status") != "granted":
            raise UnsupportedWorkflowError("Effectful browser writes require a granted approval.")

        capability_token = dispatch.get("capability_token")
        claims = dispatch.get("capability_token_claims") or {}
        if not capability_token:
            raise UnsupportedWorkflowError("Effectful browser writes require a capability token.")
        if not claims:
            raise UnsupportedWorkflowError("Effectful browser writes require capability token claims.")

        if claims.get("tenant_id") != context.tenant_id:
            raise UnsupportedWorkflowError("Capability token tenant scope does not match execution context.")
        if claims.get("workspace_id") != context.workspace_id:
            raise UnsupportedWorkflowError("Capability token workspace scope does not match execution context.")
        if claims.get("session_id") != context.session_id:
            raise UnsupportedWorkflowError("Capability token session scope does not match execution context.")
        if claims.get("action_id") != context.action_id:
            raise UnsupportedWorkflowError("Capability token action scope does not match execution context.")
        if claims.get("tool_id") != fixture.get("tool_id"):
            raise UnsupportedWorkflowError("Capability token tool scope does not match fixture tool.")
        if claims.get("issued_to_worker_kind") != context.worker_kind:
            raise UnsupportedWorkflowError("Capability token worker scope does not match browser worker.")
        if int(claims.get("lease_epoch", context.lease_epoch)) != int(context.lease_epoch):
            raise UnsupportedWorkflowError("Capability token lease epoch does not match execution context.")
        if dispatch.get("approved_argument_digest") and claims.get("approved_argument_digest") != dispatch.get(
            "approved_argument_digest"
        ):
            raise UnsupportedWorkflowError("Capability token approved argument digest does not match dispatch input.")

        expires_at = claims.get("expires_at")
        if expires_at is not None:
            expires = datetime.fromisoformat(expires_at.replace("Z", "+00:00"))
            if expires <= datetime.now(UTC):
                raise UnsupportedWorkflowError("Capability token is expired.")

        required_scopes = self._required_scopes_for_tool(fixture["tool_id"])
        token_scopes = set(claims.get("scopes", []))
        if not required_scopes.issubset(token_scopes):
            raise UnsupportedWorkflowError("Capability token scopes are insufficient for this mutation flow.")

    async def _run_step(
        self,
        *,
        context: WorkerExecutionContext,
        created_at: str,
        fixture: dict[str, Any],
        artifacts: list[ArtifactRecord],
        handle: BrowserHandleState,
        observations: list[BrowserObservation],
        page: Any,
        step: dict[str, Any],
        index: int,
    ) -> BrowserObservation:
        kind = step["kind"]

        if kind == "open_context":
            return BrowserObservation(
                step_kind=kind,
                detail="opened browser context",
                data={"step_index": index, "fixture_id": fixture["id"]},
            )

        if kind == "navigate":
            target_url = step["target_url"]
            await page.goto(target_url)
            handle.current_url = target_url
            handle.stable_page_marker = f"url:{target_url}"
            handle.last_observed_at = created_at
            handle.state_ref = f"fixture:{fixture['id']}|stable:{handle.stable_page_marker}"
            return BrowserObservation(
                step_kind=kind,
                detail=f"navigated to {target_url}",
                target_url=target_url,
                data={"step_index": index},
            )

        if kind == "read":
            selector = step["selector"]
            text = await page.read(selector)
            handle.last_observed_at = created_at
            handle.stable_page_marker = f"selector:{selector}:{text.strip()[:64]}"
            handle.state_ref = f"fixture:{fixture['id']}|stable:{handle.stable_page_marker}"
            return BrowserObservation(
                step_kind=kind,
                detail=text,
                selector=selector,
                data={"step_index": index},
            )

        if kind == "extract":
            selector = step["selector"]
            extracted = await page.extract(selector)
            handle.last_observed_at = created_at
            handle.stable_page_marker = f"selector:{selector}:{str(extracted.get('text', ''))[:64]}"
            handle.state_ref = f"fixture:{fixture['id']}|stable:{handle.stable_page_marker}"
            return BrowserObservation(
                step_kind=kind,
                detail=f"extracted {selector}",
                selector=selector,
                data={"step_index": index, "extracted": extracted},
            )

        if kind == "fill":
            selector = step["selector"]
            value = step["value"]
            await page.fill(selector, value)
            handle.last_observed_at = created_at
            return BrowserObservation(
                step_kind=kind,
                detail=f"filled {selector}",
                selector=selector,
                data={"step_index": index, "value_length": len(value)},
            )

        if kind == "click":
            selector = step["selector"]
            await page.click(selector)
            handle.last_observed_at = created_at
            return BrowserObservation(
                step_kind=kind,
                detail=f"clicked {selector}",
                selector=selector,
                data={"step_index": index},
            )

        if kind == "submit":
            selector = step["selector"]
            await page.submit(selector)
            handle.last_observed_at = created_at
            return BrowserObservation(
                step_kind=kind,
                detail=f"submitted {selector}",
                selector=selector,
                data={"step_index": index},
            )

        if kind == "take_screenshot":
            artifact = await self._capture_artifact(
                context=context,
                created_at=created_at,
                artifacts=artifacts,
                handle=handle,
                page=page,
                artifact_kind="screenshot",
            )
            return BrowserObservation(
                step_kind=kind,
                detail="captured screenshot artifact",
                artifact_kind="screenshot",
                data={"step_index": index, "artifact_id": artifact.artifact_id},
            )

        if kind == "take_dom_snapshot":
            artifact = await self._capture_artifact(
                context=context,
                created_at=created_at,
                artifacts=artifacts,
                handle=handle,
                page=page,
                artifact_kind="dom_snapshot",
            )
            return BrowserObservation(
                step_kind=kind,
                detail="captured dom snapshot artifact",
                artifact_kind="dom_snapshot",
                data={"step_index": index, "artifact_id": artifact.artifact_id},
            )

        if kind == "verify":
            expectation = step.get("expectation") or {}
            text = await page.content()
            selector = step.get("selector")
            if selector:
                text = await page.read(selector)
            elif expectation.get("artifact_kind") == "dom_snapshot":
                text = await page.content()

            expected_contains = expectation.get("contains")
            expected_equals = expectation.get("equals")
            if expected_contains is not None and expected_contains not in text:
                raise BrowserVerificationError(
                    f"Expected text containing {expected_contains!r}, got {text!r}."
                )
            if expected_equals is not None and expected_equals != text:
                raise BrowserVerificationError(
                    f"Expected text equal to {expected_equals!r}, got {text!r}."
                )
            return BrowserObservation(
                step_kind=kind,
                detail="verified expected browser state",
                selector=selector,
                data={"step_index": index, "verified_text": text},
            )

        raise UnsupportedWorkflowError(f"Unsupported step kind {kind!r}.")

    async def _capture_expected_artifacts(
        self,
        *,
        context: WorkerExecutionContext,
        created_at: str,
        fixture: dict[str, Any],
        artifacts: list[ArtifactRecord],
        handle: BrowserHandleState,
        page: Any,
        artifact_kinds: list[str],
        start_index: int,
    ) -> list[BrowserObservation]:
        observations: list[BrowserObservation] = []
        for offset, artifact_kind in enumerate(fixture.get("expected_artifacts", []), start=0):
            if artifact_kind in artifact_kinds:
                continue

            artifact = await self._capture_artifact(
                context=context,
                created_at=created_at,
                artifacts=artifacts,
                handle=handle,
                page=page,
                artifact_kind=artifact_kind,
            )
            observations.append(
                BrowserObservation(
                    step_kind=f"capture_{artifact_kind}",
                    detail=f"captured {artifact_kind} artifact",
                    artifact_kind=artifact_kind,
                    data={
                        "step_index": start_index + offset,
                        "auto_captured": True,
                        "artifact_id": artifact.artifact_id,
                    },
                )
            )
            artifact_kinds.append(artifact_kind)

        return observations

    async def _capture_named_artifacts(
        self,
        *,
        context: WorkerExecutionContext,
        created_at: str,
        fixture: dict[str, Any],
        artifacts: list[ArtifactRecord],
        handle: BrowserHandleState,
        artifact_kinds: list[str],
        page: Any,
        kinds: list[str],
        start_index: int,
    ) -> list[BrowserObservation]:
        expected = set(fixture.get("expected_artifacts", []))
        requested = [kind for kind in kinds if kind in expected and kind not in artifact_kinds]
        if not requested:
            return []

        observations: list[BrowserObservation] = []
        for offset, artifact_kind in enumerate(requested, start=0):
            artifact = await self._capture_artifact(
                context=context,
                created_at=created_at,
                artifacts=artifacts,
                handle=handle,
                page=page,
                artifact_kind=artifact_kind,
            )
            observations.append(
                BrowserObservation(
                    step_kind=f"capture_{artifact_kind}",
                    detail=f"captured {artifact_kind} artifact",
                    artifact_kind=artifact_kind,
                    data={
                        "step_index": start_index + offset,
                        "auto_captured": True,
                        "artifact_id": artifact.artifact_id,
                    },
                )
            )
            artifact_kinds.append(artifact_kind)

        return observations

    async def _capture_artifact(
        self,
        *,
        context: WorkerExecutionContext,
        created_at: str,
        artifacts: list[ArtifactRecord],
        handle: BrowserHandleState,
        page: Any,
        artifact_kind: str,
    ) -> ArtifactRecord:
        if artifact_kind in {"screenshot", "pre_write_screenshot", "post_write_screenshot"}:
            payload = await page.screenshot()
        elif artifact_kind == "dom_snapshot":
            payload = (await page.content()).encode("utf-8")
        elif artifact_kind == "trace":
            payload = f"trace:{context.session_id}:{context.action_id}:{page.url}".encode("utf-8")
        else:
            raise UnsupportedWorkflowError(f"Unsupported artifact kind {artifact_kind!r}.")

        artifact = self._artifact_store.register_bytes(
            context=context,
            artifact_kind=artifact_kind,
            payload=payload,
            created_at=created_at,
        )
        artifacts.append(artifact)
        handle.last_stable_artifact_id = artifact.artifact_id
        handle.last_observed_at = created_at
        handle.state_ref = f"{handle.browser_handle_id}:{artifact.artifact_id}"
        return artifact

    def _submit_result(
        self,
        *,
        status: str,
        artifacts: list[ArtifactRecord],
        trace_artifact_id: str | None,
        fixture: dict[str, Any],
    ) -> dict[str, Any]:
        return {
            "status": status,
            "artifact_ids": [artifact.artifact_id for artifact in artifacts],
            "trace_artifact_id": trace_artifact_id,
            "summary": {
                "tool_id": fixture.get("tool_id"),
                "mutation_class": fixture.get("mutation_class"),
                "uncertainty_trigger": fixture.get("uncertainty_trigger"),
            },
        }

    def _artifact_id_for_kind(
        self,
        artifacts: list[ArtifactRecord],
        artifact_kind: str,
    ) -> str | None:
        for artifact in artifacts:
            if artifact.artifact_kind == artifact_kind:
                return artifact.artifact_id
        return None

    def _uncertainty_triggered(self, fixture: dict[str, Any]) -> bool:
        return fixture.get("uncertainty_trigger") in {
            "submit_disconnect",
            "worker_loss_after_submit",
            "post_click_timeout",
        }

    def _required_scopes_for_tool(self, tool_id: str) -> set[str]:
        if tool_id == "browser.submit":
            return {"browser.submit", "artifact.capture"}
        if tool_id == "browser.click":
            return {"browser.click"}
        if tool_id == "browser.delete":
            return {"browser.delete"}
        return set()
