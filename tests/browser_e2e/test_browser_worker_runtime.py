import asyncio
import json
import sys
from pathlib import Path

from jsonschema import validate
import pytest
import yaml

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "py/packages"))

from aegis_browser_worker.dispatch import BrowserDispatchHandler
from aegis_browser_worker.errors import BrowserVerificationError, UnsupportedWorkflowError
from aegis_browser_worker.runner import BrowserWorkflowRunner
from aegis_browser_worker.service import BrowserWorkerService
from aegis_browser_worker.worker import BrowserWorker


class FakePage:
    def __init__(self, selector_text: dict[str, str], initial_url: str = "about:blank") -> None:
        self.url = initial_url
        self._selector_text = selector_text
        self.closed = False
        self.screenshot_calls = 0
        self.content_calls = 0

    async def goto(self, target_url: str) -> None:
        self.url = target_url

    async def read(self, selector: str) -> str:
        return self._selector_text[selector]

    async def extract(self, selector: str) -> dict[str, str]:
        return {"selector": selector, "text": self._selector_text[selector]}

    async def screenshot(self) -> bytes:
        self.screenshot_calls += 1
        return b"fake-screenshot"

    async def content(self) -> str:
        self.content_calls += 1
        return "<html><body>account summary current billing profile</body></html>"

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
    fixture = _fixture("read_only_account_lookup.yaml")
    backend = FakeBackend(
        FakePage({"[data-test='account-search']": "account summary for customer"})
    )
    service = BrowserWorkerService(runner=BrowserWorkflowRunner(backend))

    payload = asyncio.run(service.execute_fixture(fixture))

    assert payload["artifact_kinds"] == ["screenshot", "dom_snapshot"]
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
    assert payload["attributes"]["browser_baseline"] == "read_only"
    assert payload["attributes"]["provider_kind"] == "playwright"


def test_browser_worker_effectful_fixture_requires_trace_in_contract_but_is_rejected():
    fixture = _fixture("uncertain_submit_recovery.yaml")
    assert "trace" in fixture["expected_artifacts"]

    backend = FakeBackend(FakePage({"#customer-state": "ignored"}))
    runner = BrowserWorkflowRunner(backend)

    with pytest.raises(UnsupportedWorkflowError):
        asyncio.run(runner.run_fixture(fixture))


def test_browser_worker_rejects_mutating_fixture_steps():
    fixture = _fixture("effectful_billing_address_update.yaml")
    backend = FakeBackend(FakePage({"[data-test='ignored']": "ignored"}))
    runner = BrowserWorkflowRunner(backend)

    with pytest.raises(UnsupportedWorkflowError):
        asyncio.run(runner.run_fixture(fixture))


def test_browser_worker_raises_when_verify_step_cannot_prove_expected_state():
    fixture = _fixture("read_only_billing_inspection.yaml")
    backend = FakeBackend(FakePage({"[data-test='billing-panel']": "wrong panel"}))
    runner = BrowserWorkflowRunner(backend)

    with pytest.raises(BrowserVerificationError):
        asyncio.run(runner.run_fixture(fixture))
