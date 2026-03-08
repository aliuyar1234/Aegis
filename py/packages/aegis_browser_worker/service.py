from __future__ import annotations

from dataclasses import replace
from datetime import UTC, datetime
from typing import Any

from aegis_contracts_py.generated.manifest import MESSAGE_NAMES, SOURCE_DIGEST

from .artifacts import BrowserArtifactStore
from .models import WorkerExecutionContext
from .runner import BrowserWorkflowRunner


class BrowserWorkerService:
    """Phase 05 browser worker boundary over the read-only workflow runner."""

    def __init__(
        self,
        *,
        runner: BrowserWorkflowRunner,
        context: WorkerExecutionContext | None = None,
    ) -> None:
        self._runner = runner
        self._context = context or WorkerExecutionContext(worker_id="browser-worker-local")

    @property
    def context(self) -> WorkerExecutionContext:
        return self._context

    def registration_payload(self) -> dict[str, Any]:
        return {
            "worker_id": self._context.worker_id,
            "worker_kind": self._context.worker_kind,
            "worker_version": self._context.worker_version,
            "supported_contract_versions": list(self._context.supported_contract_versions),
            "advertised_capacity": self._context.advertised_capacity,
            "attributes": {
                "contract_source_digest": SOURCE_DIGEST,
                "browser_baseline": "effectful",
                "provider_kind": "playwright",
                **self._context.attributes,
            },
        }

    async def execute_fixture(self, fixture: dict[str, Any]) -> dict[str, Any]:
        fixture, context, dispatch = self._normalize_dispatch_input(fixture)
        result = await self._runner.run_fixture(fixture, context=context, dispatch=dispatch)

        artifact_events = []
        for artifact in result.artifacts:
            event_payload = BrowserArtifactStore.to_event_payload(artifact)
            if result.handle.browser_handle_id:
                event_payload.update(
                    {
                        "browser_handle_id": result.handle.browser_handle_id,
                        "browser_snapshot_ref": f"{result.handle.browser_handle_id}:{artifact.artifact_id}",
                        "page_ref": result.handle.page_ref,
                        "current_url": result.handle.current_url,
                        "restart_hint": result.handle.restart_hint,
                        "provider_kind": result.handle.provider_kind,
                        "read_only_baseline_complete": result.handle.read_only_baseline_complete,
                    }
                )
            artifact_events.append(event_payload)

        return {
            "fixture_id": result.fixture_id,
            "contract_source_digest": SOURCE_DIGEST,
            "known_messages": len(MESSAGE_NAMES),
            "status": result.status,
            "policy_decision": result.policy_decision,
            "final_url": result.final_url,
            "uncertain_side_effect": result.uncertain_side_effect,
            "uncertainty_trigger": result.uncertainty_trigger,
            "requires_operator_takeover": result.requires_operator_takeover,
            "trace_artifact_id": result.trace_artifact_id,
            "submit_result": result.submit_result,
            "artifact_kinds": result.artifact_kinds,
            "artifacts": [
                BrowserArtifactStore.to_metadata_payload(artifact)
                for artifact in result.artifacts
            ],
            "artifact_uploads": [
                {
                    "artifact_id": artifact.artifact_id,
                    "storage_ref": artifact.storage_ref,
                    "upload_target": {
                        "method": artifact.upload_target.method,
                        "url": artifact.upload_target.url,
                        "headers": artifact.upload_target.headers,
                    },
                }
                for artifact in result.artifacts
            ],
            "artifact_registration_events": artifact_events,
            "handle": {
                "browser_handle_id": result.handle.browser_handle_id,
                "provider_kind": result.handle.provider_kind,
                "provider_session_ref": result.handle.provider_session_ref,
                "page_ref": result.handle.page_ref,
                "state_ref": result.handle.state_ref,
                "last_stable_artifact_id": result.handle.last_stable_artifact_id,
                "read_only_baseline_complete": result.handle.read_only_baseline_complete,
                "current_url": result.handle.current_url,
                "stable_page_marker": result.handle.stable_page_marker,
                "last_observed_at": result.handle.last_observed_at,
                "recovery_attempts": result.handle.recovery_attempts,
                "restart_hint": result.handle.restart_hint,
            },
            "recovery": {
                "stable_page_marker": result.recovery.stable_page_marker,
                "artifact_ids": result.recovery.artifact_ids,
                "restart_hint": result.recovery.restart_hint,
                "checkpoint_browser_handle": result.recovery.checkpoint_browser_handle,
                "checkpoint_browser_handles": result.recovery.checkpoint_browser_handles,
            },
            "completed_at": datetime.now(UTC).isoformat(),
            "observations": [
                {
                    "step_kind": item.step_kind,
                    "detail": item.detail,
                    "selector": item.selector,
                    "target_url": item.target_url,
                    "artifact_kind": item.artifact_kind,
                    "data": item.data,
                }
                for item in result.observations
            ],
        }

    def _normalize_dispatch_input(
        self,
        dispatch_input: dict[str, Any],
    ) -> tuple[dict[str, Any], WorkerExecutionContext, dict[str, Any]]:
        if "fixture" not in dispatch_input:
            return dispatch_input, self._context, {}

        context_overrides = dispatch_input.get("context", {})
        context = replace(self._context, **context_overrides)
        dispatch = {
            key: value
            for key, value in dispatch_input.items()
            if key not in {"fixture", "context"}
        }
        return dispatch_input["fixture"], context, dispatch
