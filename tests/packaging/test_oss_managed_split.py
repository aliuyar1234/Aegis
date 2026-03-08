from pathlib import Path
import json

import yaml
from jsonschema import validate

ROOT = Path(__file__).resolve().parents[2]


def load_yaml(path: str):
    return yaml.safe_load((ROOT / path).read_text(encoding="utf-8"))


def load_schema(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_phase12_docs_and_artifacts_exist():
    required_paths = [
        "docs/exec-plans/active/PHASE-12-oss-vs-cloud.md",
        "docs/design-docs/oss-managed-split.md",
        "docs/design-docs/deployment-flavors.md",
        "docs/design-docs/oss-managed-release-policy.md",
        "docs/references/packaging-matrix.md",
        "docs/references/release-upgrade-matrix.md",
        "meta/oss-core-manifest.yaml",
        "meta/managed-surface-catalog.yaml",
        "meta/deployment-flavors.yaml",
        "meta/split-release-policy.yaml",
        "meta/split-release-manifest.yaml",
        "tests/phase-gates/oss-managed-split.yaml",
    ]

    for path in required_paths:
        assert (ROOT / path).exists(), path


def test_phase12_machine_readable_artifacts_validate_against_schemas():
    schema_pairs = [
        ("meta/oss-core-manifest.yaml", "schema/jsonschema/oss-core-manifest.schema.json"),
        (
            "meta/managed-surface-catalog.yaml",
            "schema/jsonschema/managed-surface-catalog.schema.json",
        ),
        ("meta/deployment-flavors.yaml", "schema/jsonschema/deployment-flavors.schema.json"),
        ("meta/split-release-policy.yaml", "schema/jsonschema/split-release-policy.schema.json"),
        ("meta/split-release-manifest.yaml", "schema/jsonschema/split-release-manifest.schema.json"),
    ]

    for payload_path, schema_path in schema_pairs:
        validate(load_yaml(payload_path), load_schema(schema_path))


def test_phase12_suite_registry_matches_pytest_contract():
    suites = load_yaml("meta/test-suites.yaml")["test_suites"]
    suite = next(item for item in suites if item["id"] == "TS-016")

    assert suite["command"] == "pytest tests/packaging -q"
    assert "tests/packaging" in suite["paths"]
    assert "meta/oss-core-manifest.yaml" in suite["paths"]
    assert "meta/managed-surface-catalog.yaml" in suite["paths"]
    assert "meta/deployment-flavors.yaml" in suite["paths"]
    assert "meta/split-release-policy.yaml" in suite["paths"]
    assert "meta/split-release-manifest.yaml" in suite["paths"]
    assert "docs/design-docs/oss-managed-split.md" in suite["paths"]
    assert "docs/references/release-upgrade-matrix.md" in suite["paths"]


def test_phase12_gate_references_concrete_split_artifacts():
    gate = load_yaml("tests/phase-gates/oss-managed-split.yaml")
    fixtures = set(gate["fixtures"])
    step_ids = {step["id"] for step in gate["steps"]}

    assert gate["tests"] == ["TS-016"]
    assert set(gate["acceptance"]) == {"AC-049", "AC-050", "AC-051"}
    assert "meta/oss-core-manifest.yaml" in fixtures
    assert "meta/managed-surface-catalog.yaml" in fixtures
    assert "meta/deployment-flavors.yaml" in fixtures
    assert "meta/split-release-policy.yaml" in fixtures
    assert "meta/split-release-manifest.yaml" in fixtures
    assert "schema/jsonschema/oss-core-manifest.schema.json" in fixtures
    assert "schema/jsonschema/deployment-flavors.schema.json" in fixtures
    assert {"surface-boundary", "deployment-flavors", "release-policy"} <= step_ids


def test_oss_core_boundary_and_managed_catalog_are_explicit():
    oss_manifest = load_yaml("meta/oss-core-manifest.yaml")
    managed_catalog = load_yaml("meta/managed-surface-catalog.yaml")

    assert "aegis_runtime" in oss_manifest["oss_core"]["control_plane_apps"]
    assert "aegis_events" in oss_manifest["oss_core"]["control_plane_apps"]
    assert "py/packages/aegis_browser_worker" in oss_manifest["oss_core"]["execution_plane_packages"]
    assert "shared_cloud" in oss_manifest["bounded_exclusions"]["deployment_flavors_not_included"]
    assert "hosted tenant provisioning service" in oss_manifest["bounded_exclusions"]["managed_control_plane_services"]
    assert "managed audit export connectors" in oss_manifest["bounded_exclusions"]["managed_control_plane_services"]

    managed_ids = {item["id"] for item in managed_catalog["managed_surfaces"]}
    assert managed_ids == {
        "shared-cloud-control-plane",
        "isolated-execution-routing",
        "managed-operations",
        "dedicated-deployment-management",
        "enterprise-integrations",
    }

    dedicated = next(
        item
        for item in managed_catalog["managed_surfaces"]
        if item["id"] == "dedicated-deployment-management"
    )
    assert "dedicated_deployment" in dedicated["included_flavors"]
    assert "aegis_runtime" in dedicated["depends_on_oss_core"]


def test_deployment_flavors_and_release_manifest_cover_all_flavors():
    flavors = load_yaml("meta/deployment-flavors.yaml")["flavors"]
    release_lines = load_yaml("meta/split-release-manifest.yaml")["release_lines"]

    flavor_ids = [item["id"] for item in flavors]
    release_flavors = [item["flavor"] for item in release_lines]

    assert flavor_ids == [
        "oss_local",
        "shared_cloud",
        "isolated_execution",
        "dedicated_deployment",
    ]
    assert release_flavors == flavor_ids

    isolated = next(item for item in flavors if item["id"] == "isolated_execution")
    dedicated = next(item for item in flavors if item["id"] == "dedicated_deployment")

    assert isolated["worker_pool_mode"] == "tenant_isolated"
    assert isolated["artifact_isolation"] == "tenant_dedicated_keyspace"
    assert dedicated["control_plane_mode"] == "dedicated"
    assert dedicated["support_boundary"] == "dedicated_control_plane"

    for release_line in release_lines:
        assert "tests/phase-gates/oss-managed-split.yaml" in release_line["gate_refs"]
        for path in release_line["required_docs"]:
            assert (ROOT / path).exists(), path


def test_split_release_policy_covers_contracts_migrations_and_docs():
    policy = load_yaml("meta/split-release-policy.yaml")
    policy_doc = (ROOT / "docs/design-docs/oss-managed-release-policy.md").read_text(encoding="utf-8").lower()
    split_doc = (ROOT / "docs/design-docs/oss-managed-split.md").read_text(encoding="utf-8").lower()
    flavor_doc = (ROOT / "docs/design-docs/deployment-flavors.md").read_text(encoding="utf-8").lower()
    packaging_doc = (ROOT / "docs/references/packaging-matrix.md").read_text(encoding="utf-8").lower()
    release_doc = (ROOT / "docs/references/release-upgrade-matrix.md").read_text(encoding="utf-8").lower()

    assert policy["contract_policy"]["runtime_contracts"]["breaking_change_requires_explicit_version_bump"] is True
    assert policy["contract_policy"]["tool_io_schemas"]["managed_only_schema_fork_forbidden"] is True
    assert policy["operator_documentation_obligations"]["require_console_docs_for_surface_changes"] is True
    assert policy["split_guardrails"]["all_flavors_covered_by_packaging_and_release_matrices"] is True

    assert "managed-only control-plane services, packages, and operational features" in split_doc
    assert "shared cloud" in flavor_doc
    assert "isolated execution" in flavor_doc
    assert "dedicated deployment" in flavor_doc
    assert "contracts, migrations, and operator-facing documentation obligations" in policy_doc
    assert "oss local" in packaging_doc
    assert "release owner" in release_doc
    assert "upgrade strategy" in release_doc
