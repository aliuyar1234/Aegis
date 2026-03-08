from __future__ import annotations

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
                "browser_baseline": "read_only",
                "provider_kind": "playwright",
                **self._context.attributes,
            },
        }

    async def execute_fixture(self, fixture: dict[str, Any]) -> dict[str, Any]:
        result = await self._runner.run_fixture(fixture, context=self._context)
        return {
            "fixture_id": result.fixture_id,
            "contract_source_digest": SOURCE_DIGEST,
            "known_messages": len(MESSAGE_NAMES),
            "policy_decision": result.policy_decision,
            "final_url": result.final_url,
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
            "artifact_registration_events": [
                BrowserArtifactStore.to_event_payload(artifact)
                for artifact in result.artifacts
            ],
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
