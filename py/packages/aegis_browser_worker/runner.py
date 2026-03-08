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
    BrowserRecoveryPoint,
    BrowserWorkflowResult,
    MUTATING_STEP_KINDS,
    READ_ONLY_STEP_KINDS,
    WorkerExecutionContext,
)
from .protocols import BrowserAutomationBackend
from .recovery import BrowserRecoverySerializer


class BrowserWorkflowRunner:
    """Executes the Phase 05 read-only browser workflow baseline."""

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
    ) -> BrowserWorkflowResult:
        context = context or WorkerExecutionContext(worker_id="browser-worker-local")
        self._validate_fixture(fixture)
        session = await self._backend.open_session(read_only=True)
        page = await session.new_page()
        observations: list[BrowserObservation] = []
        artifact_kinds: list[str] = []
        artifacts: list[ArtifactRecord] = []

        try:
            created_at = datetime.now(UTC).isoformat()
            handle = BrowserHandleState(
                browser_handle_id=f"browser-handle-{uuid4().hex}",
                provider_kind="playwright",
                provider_session_ref=session.session_ref,
                page_ref=session.page_ref,
                state_ref=f"fixture:{fixture['id']}",
                last_observed_at=created_at,
                restart_hint=f"reattach:{fixture['id']}",
            )

            for index, step in enumerate(fixture["steps"], start=1):
                observation = await self._run_step(
                    context=context,
                    created_at=created_at,
                    fixture=fixture,
                    artifacts=artifacts,
                    handle=handle,
                    observations=observations,
                    page=page,
                    step=step,
                    index=index,
                )
                observations.append(observation)
                if observation.artifact_kind is not None:
                    artifact_kinds.append(observation.artifact_kind)

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
            return BrowserWorkflowResult(
                fixture_id=fixture["id"],
                handle=handle,
                observations=observations,
                artifact_kinds=artifact_kinds,
                artifacts=artifacts,
                recovery=recovery,
                final_url=page.url,
                policy_decision=fixture.get("expected_policy_decision"),
            )
        finally:
            await page.close()
            await session.close()

    def _validate_fixture(self, fixture: dict[str, Any]) -> None:
        mutation_class = fixture.get("mutation_class")
        if mutation_class != "read_only":
            raise UnsupportedWorkflowError(
                f"Phase 05 worker only supports read_only fixtures, got {mutation_class!r}."
            )
        if fixture.get("requires_approval"):
            raise UnsupportedWorkflowError("Phase 05 worker cannot execute approval-gated fixtures.")

        for step in fixture.get("steps", []):
            kind = step["kind"]
            if kind in MUTATING_STEP_KINDS:
                raise UnsupportedWorkflowError(
                    f"Phase 05 worker rejects mutating step kind {kind!r}."
                )
            if kind not in READ_ONLY_STEP_KINDS:
                raise UnsupportedWorkflowError(
                    f"Phase 05 worker does not recognize step kind {kind!r}."
                )

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
                detail="opened read-only browser context",
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

        if kind == "take_screenshot":
            screenshot = await page.screenshot()
            artifact = self._artifact_store.register_bytes(
                context=context,
                artifact_kind="screenshot",
                payload=screenshot,
                created_at=created_at,
            )
            artifacts.append(artifact)
            handle.last_stable_artifact_id = artifact.artifact_id
            handle.last_observed_at = created_at
            return BrowserObservation(
                step_kind=kind,
                detail="captured screenshot artifact",
                artifact_kind="screenshot",
                data={"step_index": index, "artifact_id": artifact.artifact_id},
            )

        if kind == "take_dom_snapshot":
            dom_snapshot = (await page.content()).encode("utf-8")
            artifact = self._artifact_store.register_bytes(
                context=context,
                artifact_kind="dom_snapshot",
                payload=dom_snapshot,
                created_at=created_at,
            )
            artifacts.append(artifact)
            handle.last_stable_artifact_id = artifact.artifact_id
            handle.last_observed_at = created_at
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
            elif observations:
                for prior in reversed(observations):
                    if prior.detail:
                        text = prior.detail
                        break

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

            index = start_index + offset
            if artifact_kind == "screenshot":
                artifact = self._artifact_store.register_bytes(
                    context=context,
                    artifact_kind="screenshot",
                    payload=await page.screenshot(),
                    created_at=created_at,
                )
                artifacts.append(artifact)
                handle.last_stable_artifact_id = artifact.artifact_id
                observations.append(
                    BrowserObservation(
                        step_kind="take_screenshot",
                        detail="captured screenshot artifact",
                        artifact_kind="screenshot",
                        data={
                            "step_index": index,
                            "auto_captured": True,
                            "artifact_id": artifact.artifact_id,
                        },
                    )
                )
                artifact_kinds.append("screenshot")
                continue

            if artifact_kind == "dom_snapshot":
                artifact = self._artifact_store.register_bytes(
                    context=context,
                    artifact_kind="dom_snapshot",
                    payload=(await page.content()).encode("utf-8"),
                    created_at=created_at,
                )
                artifacts.append(artifact)
                handle.last_stable_artifact_id = artifact.artifact_id
                observations.append(
                    BrowserObservation(
                        step_kind="take_dom_snapshot",
                        detail="captured dom snapshot artifact",
                        artifact_kind="dom_snapshot",
                        data={
                            "step_index": index,
                            "auto_captured": True,
                            "artifact_id": artifact.artifact_id,
                        },
                    )
                )
                artifact_kinds.append("dom_snapshot")
                continue

            if artifact_kind == "trace":
                artifact = self._artifact_store.register_bytes(
                    context=context,
                    artifact_kind="trace",
                    payload=f"trace:{fixture['id']}:{page.url}".encode("utf-8"),
                    created_at=created_at,
                )
                artifacts.append(artifact)
                observations.append(
                    BrowserObservation(
                        step_kind="capture_trace",
                        detail="captured trace artifact",
                        artifact_kind="trace",
                        data={
                            "step_index": index,
                            "auto_captured": True,
                            "artifact_id": artifact.artifact_id,
                        },
                    )
                )
                artifact_kinds.append("trace")
                continue

        return observations
