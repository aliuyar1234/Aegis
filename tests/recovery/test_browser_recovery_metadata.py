import asyncio
import json
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path

from jsonschema import validate
import yaml

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "py/packages"))

from aegis_browser_worker.runner import BrowserWorkflowRunner
from aegis_browser_worker.service import BrowserWorkerService


CHECKPOINT_SCHEMA = json.loads(
    (ROOT / "schema/checkpoints/session-checkpoint-v1.schema.json").read_text()
)


class FakePage:
    def __init__(self) -> None:
        self.url = "about:blank"
        self._content = "<html><body>current billing profile account summary</body></html>"

    async def goto(self, target_url: str) -> None:
        self.url = target_url

    async def read(self, selector: str) -> str:
        if selector == "[data-test='billing-panel']":
            return "current billing profile"
        if selector == "#customer-state":
            return "pending manual verification"
        return "account summary"

    async def extract(self, selector: str) -> dict[str, str]:
        return {"selector": selector, "text": await self.read(selector)}

    async def click(self, selector: str) -> None:
        self._content = f"<html><body>clicked {selector}</body></html>"

    async def fill(self, selector: str, value: str) -> None:
        self._content = f"<html><body>{value}</body></html>"

    async def submit(self, selector: str) -> None:
        self._content = "<html><body>pending manual verification</body></html>"

    async def screenshot(self) -> bytes:
        return b"fake-screenshot"

    async def content(self) -> str:
        return self._content

    async def close(self) -> None:
        return None


class FakeSession:
    session_ref = "fake-session"
    page_ref = "fake-page"

    def __init__(self) -> None:
        self.page = FakePage()

    async def new_page(self) -> FakePage:
        return self.page

    async def close(self) -> None:
        return None


class FakeBackend:
    def __init__(self) -> None:
        self.read_only_calls: list[bool] = []

    async def open_session(self, *, read_only: bool) -> FakeSession:
        self.read_only_calls.append(read_only)
        return FakeSession()


def _fixture(name: str) -> dict:
    return yaml.safe_load((ROOT / "tests/browser_e2e/fixtures" / name).read_text())


def _dispatch_input(fixture: dict, action_id: str) -> dict:
    return {
        "fixture": fixture,
        "context": {
            "tenant_id": "tenant-local",
            "workspace_id": "workspace-local",
            "session_id": "session-local",
            "action_id": action_id,
            "lease_epoch": 1,
        },
        "approval_status": "granted",
        "capability_token": "aegis.ctk.v1.test-token",
        "approved_argument_digest": "approved-digest-1",
        "capability_token_claims": {
            "tenant_id": "tenant-local",
            "workspace_id": "workspace-local",
            "session_id": "session-local",
            "action_id": action_id,
            "tool_id": fixture["tool_id"],
            "approved_argument_digest": "approved-digest-1",
            "dangerous_action_class": fixture["mutation_class"],
            "expires_at": (datetime.now(UTC) + timedelta(minutes=15)).isoformat().replace("+00:00", "Z"),
            "lease_epoch": 1,
            "scopes": ["browser.submit", "artifact.capture"],
            "issued_to_worker_kind": "browser",
        },
    }


def test_recovery_bundle_produces_checkpoint_compatible_browser_handle():
    fixture = _fixture("read_only_billing_inspection.yaml")
    service = BrowserWorkerService(runner=BrowserWorkflowRunner(FakeBackend()))

    payload = asyncio.run(service.execute_fixture(fixture))

    checkpoint_payload = {
        "version": 1,
        "tenant_id": "tenant-local",
        "workspace_id": "workspace-local",
        "session_id": "session-local",
        "phase": "active",
        "control_mode": "autonomous",
        "health": "healthy",
        "wait_reason": "none",
        "lease_epoch": 1,
        "last_seq_no": 1,
        "latest_checkpoint_id": None,
        "action_ledger": [],
        "pending_approvals": [],
        "deadlines": [],
        "child_agents": [],
        "browser_handles": payload["recovery"]["checkpoint_browser_handles"],
        "summary_capsule": {
            "planner_summary": "browser baseline",
            "salient_facts": [],
            "operator_notes": [],
        },
        "artifact_ids": payload["recovery"]["artifact_ids"],
        "fenced": False,
    }

    validate(checkpoint_payload, CHECKPOINT_SCHEMA)
    assert payload["recovery"]["stable_page_marker"].startswith("selector:")
    assert (
        payload["recovery"]["checkpoint_browser_handle"]["last_stable_artifact_id"]
        in payload["recovery"]["artifact_ids"]
    )
    assert payload["handle"]["restart_hint"].startswith("reattach:")


def test_uncertain_effectful_recovery_keeps_last_stable_artifact_and_takeover_marker():
    fixture = _fixture("uncertain_submit_recovery.yaml")
    backend = FakeBackend()
    service = BrowserWorkerService(runner=BrowserWorkflowRunner(backend))

    payload = asyncio.run(service.execute_fixture(_dispatch_input(fixture, "action-uncertain-1")))

    assert backend.read_only_calls == [False]
    assert payload["status"] == "uncertain"
    assert payload["requires_operator_takeover"] is True
    assert payload["trace_artifact_id"] in payload["recovery"]["artifact_ids"]
    assert payload["handle"]["last_stable_artifact_id"] in payload["recovery"]["artifact_ids"]
    assert payload["recovery"]["checkpoint_browser_handle"]["last_stable_artifact_id"] == payload["handle"][
        "last_stable_artifact_id"
    ]
