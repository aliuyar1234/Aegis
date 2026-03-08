from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


READ_ONLY_STEP_KINDS = {
    "open_context",
    "navigate",
    "read",
    "extract",
    "verify",
    "take_screenshot",
    "take_dom_snapshot",
}

MUTATING_STEP_KINDS = {"click", "fill", "submit"}


@dataclass(slots=True)
class WorkerExecutionContext:
    worker_id: str
    worker_kind: str = "browser"
    worker_version: str = "0.1.0"
    supported_contract_versions: tuple[str, ...] = ("v1",)
    advertised_capacity: int = 1
    attributes: dict[str, str] = field(default_factory=dict)
    tenant_id: str = "tenant-local"
    workspace_id: str = "workspace-local"
    session_id: str = "session-local"
    action_id: str | None = None


@dataclass(slots=True)
class BrowserHandleState:
    browser_handle_id: str
    provider_kind: str = "playwright"
    provider_session_ref: str | None = None
    page_ref: str | None = None
    state_ref: str | None = None
    last_stable_artifact_id: str | None = None
    read_only_baseline_complete: bool = False
    current_url: str | None = None
    stable_page_marker: str | None = None
    last_observed_at: str | None = None
    recovery_attempts: int = 0
    restart_hint: str | None = None


@dataclass(slots=True)
class BrowserObservation:
    step_kind: str
    detail: str
    selector: str | None = None
    target_url: str | None = None
    artifact_kind: str | None = None
    data: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class BrowserWorkflowResult:
    fixture_id: str
    handle: BrowserHandleState
    observations: list[BrowserObservation]
    artifact_kinds: list[str]
    artifacts: list["ArtifactRecord"]
    recovery: "BrowserRecoveryPoint"
    final_url: str | None
    policy_decision: str | None


@dataclass(slots=True)
class ArtifactUploadTarget:
    method: str
    url: str
    headers: dict[str, str]


@dataclass(slots=True)
class ArtifactRecord:
    artifact_id: str
    tenant_id: str
    workspace_id: str
    session_id: str
    action_id: str | None
    artifact_kind: str
    sha256: str
    content_type: str
    size_bytes: int
    retention_class: str
    redaction_state: str
    object_key: str
    created_at: str
    upload_target: ArtifactUploadTarget
    storage_ref: str


@dataclass(slots=True)
class BrowserRecoveryPoint:
    browser_handle: BrowserHandleState
    stable_page_marker: str
    artifact_ids: list[str]
    restart_hint: str
    checkpoint_browser_handle: dict[str, Any]
    checkpoint_browser_handles: list[dict[str, Any]]
