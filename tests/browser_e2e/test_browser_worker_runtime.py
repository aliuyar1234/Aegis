import asyncio
import json
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path

from jsonschema import validate
import pytest
import yaml

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "py/packages"))

from aegis_browser_worker.dispatch import BrowserDispatchHandler
from aegis_browser_worker.errors import BrowserVerificationError, UnsupportedWorkflowError
from aegis_browser_worker.models import WorkerExecutionContext
from aegis_browser_worker.runner import BrowserWorkflowRunner
from aegis_browser_worker.service import BrowserWorkerService
from aegis_browser_worker.worker import BrowserWorker


class FakePage:
    def __init__(self, selector_text: dict[str, str], initial_url: str = "about:blank") -> None:
        self.url = initial_url
        self._selector_text = dict(selector_text)
        self.closed = False
        self.screenshot_calls = 0
        self.content_calls = 0
        self.fills: list[tuple[str, str]] = []
        self.clicks: list[str] = []
        self.submits: list[str] = []
        self._content = "<html><body>account summary current billing profile</body></html>"

    async def goto(self, target_url: str) -> None:
        self.url = target_url

    async def read(self, selector: str) -> str:
        return self._selector_text[selector]

    async def extract(self, selector: str) -> dict[str, str]:
        return {"selector": selector, "text": self._selector_text[selector]}

    async def click(self, selector: str) -> None:
        self.clicks.append(selector)
        self._content = "<html><body>entitlement revoked</body></html>"

    async def fill(self, selector: str, value: str) -> None:
        self.fills.append((selector, value))
        self._selector_text[selector] = value

    async def submit(self, selector: str) -> None:
        self.submits.append(selector)
        if self.fills and self.fills[-1][1] == "pending manual verification":
            self._content = "<html><body>pending manual verification</body></html>"
        else:
            self._content = "<html><body>updated billing address</body></html>"

    async def screenshot(self) -> bytes:
        self.screenshot_calls += 1
        return b"fake-screenshot"

    async def content(self) -> str:
        self.content_calls += 1
        return self._content

    async def close(self) -> None:
        self.closed = True


class FakeSession:
    def __init__(self, page: FakePage) -> None:
        self.session_ref = "fake-session"
        self.page_ref = "fake-page"
        self._page = page
        self.closed = False

    async def new_page(self) -> FakePage:
        return self._page

    async def close(self) -> None:
        self.closed = True


class FakeBackend:
    def __init__(self, page: FakePage) -> None:
        self.page = page
        self.session = FakeSession(page)
        self.read_only_calls: list[bool] = []

    async def open_session(self, *, read_only: bool) -> FakeSession:
        self.read_only_calls.append(read_only)
        return self.session


def _fixture(name: str) -> dict:
    return yaml.safe_load((ROOT / "tests/browser_e2e/fixtures" / name).read_text())


ARTIFACT_METADATA_SCHEMA = json.loads(
    (ROOT / "schema/jsonschema/artifact-metadata.schema.json").read_text()
)
ARTIFACT_REGISTERED_SCHEMA = json.loads(
    (ROOT / "schema/event-payloads/artifact_registered.schema.json").read_text()
)
BROWSER_SUBMIT_OUTPUT_SCHEMA = json.loads(
    (ROOT / "schema/jsonschema/browser-submit-output.schema.json").read_text()
)


def _dispatch_input(
    fixture: dict,
    *,
    action_id: str = "action-browser-1",
    approval_status: str = "granted",
    capability_token: str = "aegis.ctk.v1.test-token",
    expires_at: str | None = None,
) -> dict:
    return {
        "fixture": fixture,
        "context": {
            "tenant_id": "tenant-browser",
            "workspace_id": "workspace-browser",
            "session_id": "session-browser",
            "action_id": action_id,
            "lease_epoch": 7,
        },
        "approval_status": approval_status,
        "capability_token": capability_token,
        "approved_argument_digest": "approved-digest-1",
        "capability_token_claims": {
            "tenant_id": "tenant-browser",
            "workspace_id": "workspace-browser",
            "session_id": "session-browser",
            "action_id": action_id,
            "tool_id": fixture.get("tool_id"),
            "approved_argument_digest": "approved-digest-1",
            "dangerous_action_class": fixture.get("mutation_class"),
            "expires_at": expires_at
            or (datetime.now(UTC) + timedelta(minutes=15)).isoformat().replace("+00:00", "Z"),
            "lease_epoch": 7,
            "scopes": ["browser.submit", "artifact.capture", "browser.click", "browser.delete"],
            "issued_to_worker_kind": "browser",
        },
    }


def test_browser_worker_runs_read_only_fixture_and_marks_handle_complete():
    fixture = _fixture("read_only_account_lookup.yaml")
    backend = FakeBackend(
        FakePage({"[data-test='account-search']": "account summary for customer"})
    )
    service = BrowserWorkerService(runner=BrowserWorkflowRunner(backend))
    worker = BrowserWorker(
        dispatch_handler=BrowserDispatchHandler(service),
        service=service,
    )

    payload = asyncio.run(worker.handle_dispatch(fixture))

    assert backend.read_only_calls == [True]
    assert payload["status"] == "completed"
    assert payload["policy_decision"] == "allow"
    assert payload["artifact_kinds"] == ["screenshot", "dom_snapshot"]
    assert payload["handle"]["read_only_baseline_complete"] is True
    assert payload["handle"]["provider_kind"] == "playwright"
    assert payload["final_url"] == "https://admin.example.local/accounts"
    assert payload["handle"]["stable_page_marker"].startswith("selector:")
    assert payload["recovery"]["checkpoint_browser_handle"]["read_only_baseline_complete"] is True
    assert any(item["step_kind"] == "verify" for item in payload["observations"])
    assert payload["recovery"]["artifact_ids"] == [
        artifact["artifact_id"] for artifact in payload["artifacts"]
    ]


def test_browser_worker_artifact_payloads_validate_against_locked_schemas():
    fixture = _fixture("effectful_billing_address_update.yaml")
    backend = FakeBackend(FakePage({"#billing-address": "pending"}))
    service = BrowserWorkerService(runner=BrowserWorkflowRunner(backend))

    payload = asyncio.run(service.execute_fixture(_dispatch_input(fixture)))

    assert payload["status"] == "submitted"
    assert {
        "pre_write_screenshot",
        "post_write_screenshot",
        "dom_snapshot",
        "trace",
    }.issubset(set(payload["artifact_kinds"]))
    validate(payload["submit_result"], BROWSER_SUBMIT_OUTPUT_SCHEMA)

    for artifact in payload["artifacts"]:
        validate(artifact, ARTIFACT_METADATA_SCHEMA)
        assert artifact["sha256"]
        assert artifact["size_bytes"] > 0

    for upload in payload["artifact_uploads"]:
        assert upload["upload_target"]["method"] == "PUT"
        assert upload["upload_target"]["url"].startswith("https://object-store.local/")
        assert upload["storage_ref"].startswith("s3://")

    for event_payload in payload["artifact_registration_events"]:
        validate(event_payload, ARTIFACT_REGISTERED_SCHEMA)
        assert event_payload["storage_ref"].startswith("s3://")


def test_browser_worker_registration_payload_marks_browser_worker_kind():
    backend = FakeBackend(FakePage({"[data-test='account-search']": "account summary"}))
    service = BrowserWorkerService(runner=BrowserWorkflowRunner(backend))
    worker = BrowserWorker(
        dispatch_handler=BrowserDispatchHandler(service),
        service=service,
    )

    payload = worker.registration_payload()

    assert payload["worker_kind"] == "browser"
    assert payload["attributes"]["browser_baseline"] == "effectful"
    assert payload["attributes"]["provider_kind"] == "playwright"


def test_browser_worker_executes_approval_bound_submit_flow():
    fixture = _fixture("effectful_billing_address_update.yaml")
    backend = FakeBackend(FakePage({"#billing-address": "pending"}))
    runner = BrowserWorkflowRunner(backend)
    dispatch_input = _dispatch_input(fixture)

    payload = asyncio.run(
        runner.run_fixture(
            fixture,
            context=WorkerExecutionContext(
                worker_id="browser-worker-local",
                tenant_id="tenant-browser",
                workspace_id="workspace-browser",
                session_id="session-browser",
                action_id="action-browser-1",
                lease_epoch=7,
            ),
            dispatch=dispatch_input,
        )
    )

    assert backend.read_only_calls == [False]
    assert payload.status == "submitted"
    assert payload.policy_decision == "require_approval"
    assert payload.uncertain_side_effect is False
    assert {
        "pre_write_screenshot",
        "post_write_screenshot",
        "dom_snapshot",
        "trace",
    }.issubset(set(payload.artifact_kinds))
    assert payload.submit_result["status"] == "submitted"
    assert any(item.step_kind == "submit" for item in payload.observations)


def test_browser_worker_returns_rejected_payload_for_denied_mutation_fixture():
    fixture = _fixture("effectful_entitlement_revoke.yaml")
    backend = FakeBackend(FakePage({"[data-test='revoke-entitlement']": "pending"}))
    service = BrowserWorkerService(runner=BrowserWorkflowRunner(backend))

    payload = asyncio.run(service.execute_fixture(fixture))

    assert backend.read_only_calls == []
    assert payload["status"] == "rejected"
    assert payload["policy_decision"] == "deny"
    assert payload["artifact_kinds"] == []
    assert payload["submit_result"]["status"] == "rejected"
    assert payload["observations"][0]["step_kind"] == "policy_rejected"


def test_browser_worker_requires_capability_token_for_effectful_write():
    fixture = _fixture("effectful_billing_address_update.yaml")
    backend = FakeBackend(FakePage({"#billing-address": "pending"}))
    runner = BrowserWorkflowRunner(backend)
    dispatch_input = _dispatch_input(fixture)
    dispatch_input["capability_token"] = ""

    with pytest.raises(UnsupportedWorkflowError):
        asyncio.run(runner.run_fixture(fixture, dispatch=dispatch_input))


def test_browser_worker_marks_uncertain_submit_for_operator_takeover():
    fixture = _fixture("uncertain_submit_recovery.yaml")
    backend = FakeBackend(FakePage({"#customer-state": "pending manual verification"}))
    service = BrowserWorkerService(runner=BrowserWorkflowRunner(backend))

    payload = asyncio.run(service.execute_fixture(_dispatch_input(fixture, action_id="action-uncertain-1")))

    assert backend.read_only_calls == [False]
    assert payload["status"] == "uncertain"
    assert payload["uncertain_side_effect"] is True
    assert payload["uncertainty_trigger"] == "worker_loss_after_submit"
    assert payload["requires_operator_takeover"] is True
    assert payload["trace_artifact_id"] in payload["submit_result"]["artifact_ids"]
    assert payload["submit_result"]["status"] == "uncertain"


def test_browser_worker_raises_when_verify_step_cannot_prove_expected_state():
    fixture = _fixture("read_only_billing_inspection.yaml")
    backend = FakeBackend(FakePage({"[data-test='billing-panel']": "wrong panel"}))
    backend.page._content = "<html><body>wrong panel</body></html>"
    runner = BrowserWorkflowRunner(backend)

    with pytest.raises(BrowserVerificationError):
        asyncio.run(runner.run_fixture(fixture))
