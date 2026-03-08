from pathlib import Path
import json

import yaml
from jsonschema import validate

ROOT = Path(__file__).resolve().parents[2]


def load_yaml(path: str):
    return yaml.safe_load((ROOT / path).read_text(encoding="utf-8"))


def load_schema(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_enterprise_docs_artifacts_and_runbooks_exist():
    required_paths = [
        "docs/exec-plans/active/PHASE-13-cloud-enterprise.md",
        "docs/design-docs/audit-export-redaction.md",
        "docs/design-docs/dedicated-deployment-isolation.md",
        "docs/design-docs/retention-and-slo-policy.md",
        "docs/threat-models/enterprise-control-matrix.md",
        "docs/runbooks/audit-export-backlog.md",
        "docs/runbooks/dedicated-key-isolation.md",
        "docs/runbooks/retention-backlog.md",
        "meta/audit-export-policy.yaml",
        "meta/dedicated-deployment-profile.yaml",
        "meta/retention-slo-policy.yaml",
        "meta/enterprise-acceptance-checklist.yaml",
        "meta/enterprise-control-matrix.yaml",
        "meta/dedicated-tenant-evidence.yaml",
        "tests/phase-gates/enterprise-readiness.yaml",
        "docs/project/open-decisions.md",
    ]

    for path in required_paths:
        assert (ROOT / path).exists(), path


def test_enterprise_machine_readable_artifacts_validate_against_schemas():
    schema_pairs = [
        ("meta/audit-export-policy.yaml", "schema/jsonschema/audit-export-policy.schema.json"),
        (
            "meta/dedicated-deployment-profile.yaml",
            "schema/jsonschema/dedicated-deployment-profile.schema.json",
        ),
        ("meta/retention-slo-policy.yaml", "schema/jsonschema/retention-slo-policy.schema.json"),
        (
            "meta/enterprise-acceptance-checklist.yaml",
            "schema/jsonschema/enterprise-acceptance-checklist.schema.json",
        ),
        (
            "meta/enterprise-control-matrix.yaml",
            "schema/jsonschema/enterprise-control-matrix.schema.json",
        ),
        (
            "meta/dedicated-tenant-evidence.yaml",
            "schema/jsonschema/dedicated-tenant-evidence.schema.json",
        ),
    ]

    for payload_path, schema_path in schema_pairs:
        validate(load_yaml(payload_path), load_schema(schema_path))


def test_phase13_suite_registry_matches_enterprise_pytest_contract():
    suites = load_yaml("meta/test-suites.yaml")["test_suites"]
    suite = next(item for item in suites if item["id"] == "TS-017")

    assert suite["command"] == "pytest tests/enterprise -q"
    assert "tests/enterprise" in suite["paths"]
    assert "meta/audit-export-policy.yaml" in suite["paths"]
    assert "meta/dedicated-deployment-profile.yaml" in suite["paths"]
    assert "meta/retention-slo-policy.yaml" in suite["paths"]
    assert "meta/enterprise-acceptance-checklist.yaml" in suite["paths"]
    assert "meta/enterprise-control-matrix.yaml" in suite["paths"]
    assert "meta/dedicated-tenant-evidence.yaml" in suite["paths"]
    assert "docs/project/open-decisions.md" in suite["paths"]


def test_enterprise_phase_gate_references_concrete_controls_and_open_decisions():
    gate = load_yaml("tests/phase-gates/enterprise-readiness.yaml")
    fixtures = set(gate["fixtures"])
    step_ids = {step["id"] for step in gate["steps"]}

    assert set(gate["tests"]) == {"TS-011", "TS-017"}
    assert set(gate["acceptance"]) == {"AC-052", "AC-053", "AC-054", "AC-055", "AC-056"}
    assert "meta/dedicated-deployment-profile.yaml" in fixtures
    assert "meta/audit-export-policy.yaml" in fixtures
    assert "meta/retention-slo-policy.yaml" in fixtures
    assert "meta/enterprise-control-matrix.yaml" in fixtures
    assert "meta/dedicated-tenant-evidence.yaml" in fixtures
    assert "meta/enterprise-acceptance-checklist.yaml" in fixtures
    assert "schema/jsonschema/dedicated-tenant-evidence.schema.json" in fixtures
    assert "docs/project/open-decisions.md" in fixtures
    assert {"dedicated-isolation", "audit-redaction", "retention-slos", "control-matrix", "open-decisions"} <= step_ids


def test_enterprise_docs_make_isolation_audit_retention_and_gate_explicit():
    audit_doc = (ROOT / "docs/design-docs/audit-export-redaction.md").read_text(encoding="utf-8").lower()
    dedicated_doc = (ROOT / "docs/design-docs/dedicated-deployment-isolation.md").read_text(encoding="utf-8").lower()
    retention_doc = (ROOT / "docs/design-docs/retention-and-slo-policy.md").read_text(encoding="utf-8").lower()
    threat_doc = (ROOT / "docs/threat-models/enterprise-control-matrix.md").read_text(encoding="utf-8").lower()
    security_doc = (ROOT / "docs/operations/security.md").read_text(encoding="utf-8").lower()
    operations_doc = (ROOT / "docs/operations/operations.md").read_text(encoding="utf-8").lower()

    assert "signed urls only" in audit_doc
    assert "redacted stubs" in audit_doc
    assert "dedicated kms namespace" in dedicated_doc
    assert "data residency hooks" in dedicated_doc
    assert "retention classes" in retention_doc
    assert "redaction completion" in retention_doc
    assert "quota and admission control" in threat_doc
    assert "tiered isolation routing" in threat_doc
    assert "runbooks and operator recovery" in threat_doc
    assert "audit export bundles" in security_doc
    assert "dedicated tenant evidence" in operations_doc


def test_enterprise_artifacts_cover_dedicated_deployment_evidence_and_slo_surfaces():
    dedicated = load_yaml("meta/dedicated-deployment-profile.yaml")
    retention = load_yaml("meta/retention-slo-policy.yaml")
    evidence = load_yaml("meta/dedicated-tenant-evidence.yaml")
    checklist = load_yaml("meta/enterprise-acceptance-checklist.yaml")

    assert dedicated["tier"] == "tier_c"
    assert dedicated["key_isolation"]["kms_mode"] == "dedicated_kms_namespace"
    assert dedicated["data_residency"]["cross_region_failover"] == "operator_approved_only"
    assert evidence["tenant_tier"] == "tier_c"
    assert evidence["key_isolation_evidence"]["kms_namespace_per_tenant"] is True
    assert evidence["operational_preflight"]["release_gate"] == "enterprise_readiness"
    assert len(retention["retention_classes"]) == 5
    assert {slo["id"] for slo in retention["slos"]} == {
        "hot_replay_load",
        "audit_export_bundle_preparation",
        "redaction_completion",
        "archive_restore",
    }
    assert len(checklist["checklist"]) == 4


def test_enterprise_runbooks_failure_catalog_and_open_decisions_are_wired():
    failure_catalog = load_yaml("meta/failure-runbooks.yaml")["failures"]
    failure_ids = {item["id"]: item for item in failure_catalog}
    open_decisions = (ROOT / "docs/project/open-decisions.md").read_text(encoding="utf-8").lower()

    assert failure_ids["audit_export_backlog"]["runbook"] == "docs/runbooks/audit-export-backlog.md"
    assert failure_ids["key_isolation_degraded"]["runbook"] == "docs/runbooks/dedicated-key-isolation.md"
    assert failure_ids["retention_backlog"]["runbook"] == "docs/runbooks/retention-backlog.md"
    assert failure_ids["audit_export_backlog"]["operator_surface"] == "audit-export"

    assert "## od-001" in open_decisions
    assert "locked principle" in open_decisions
    assert ("td" + "b") not in open_decisions
    assert "chat history" not in open_decisions
