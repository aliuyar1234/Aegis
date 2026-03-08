#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import yaml
from jsonschema import validate
from jsonschema.validators import validator_for

ROOT = Path(__file__).resolve().parents[1]
PROTO_ROOT = ROOT / "schema" / "proto"
TOOL_REGISTRY_ROOT = ROOT / "schema" / "tool-registry.yaml"
TOOL_REGISTRY_GENERATED_TARGET = (
    ROOT / "apps" / "aegis_policy" / "lib" / "aegis" / "policy" / "generated" / "tool_registry.ex"
)
DANGEROUS_ACTIONS_ROOT = ROOT / "meta" / "dangerous-action-classes.yaml"
DANGEROUS_ACTIONS_GENERATED_TARGET = (
    ROOT
    / "apps"
    / "aegis_policy"
    / "lib"
    / "aegis"
    / "policy"
    / "generated"
    / "dangerous_action_catalog.ex"
)
DANGEROUS_ACTION_ROOT = ROOT / "meta" / "dangerous-action-classes.yaml"
DANGEROUS_ACTION_GENERATED_TARGET = (
    ROOT
    / "apps"
    / "aegis_policy"
    / "lib"
    / "aegis"
    / "policy"
    / "generated"
    / "dangerous_action_catalog.ex"
)
RBAC_ROLES_ROOT = ROOT / "meta" / "rbac-roles.yaml"
RBAC_ROLES_GENERATED_TARGET = (
    ROOT / "apps" / "aegis_policy" / "lib" / "aegis" / "policy" / "generated" / "rbac_roles.ex"
)
ABAC_ATTRIBUTES_ROOT = ROOT / "meta" / "abac-attributes.yaml"
ABAC_ATTRIBUTES_GENERATED_TARGET = (
    ROOT
    / "apps"
    / "aegis_policy"
    / "lib"
    / "aegis"
    / "policy"
    / "generated"
    / "abac_attributes.ex"
)
EXTENSION_MANIFEST_SCHEMA = ROOT / "schema/jsonschema/connector-manifest.schema.json"
EXTENSION_MANIFEST_FIXTURES = [
    ROOT / "tests/extensibility/fixtures/sample-connector.yaml",
    ROOT / "tests/extensibility/fixtures/sample-artifact-processor.yaml",
    ROOT / "tests/extensibility/fixtures/sample-mcp-adapter.yaml",
]
EXTENSION_COMPATIBILITY_POLICY_SCHEMA = ROOT / "schema/jsonschema/extension-compatibility-policy.schema.json"
EXTENSION_COMPATIBILITY_POLICY = ROOT / "meta/extension-compatibility-policy.yaml"
EXTENSION_PACK_MANIFEST_SCHEMA = ROOT / "schema/jsonschema/extension-pack-manifest.schema.json"
EXTENSION_PACK_MANIFEST = ROOT / "tests/extensibility/fixtures/sample-extension-pack/pack.yaml"
MEDIA_FIXTURE_SCHEMA_PAIRS = [
    (
        ROOT / "schema/jsonschema/media-sidecar-catalog.schema.json",
        ROOT / "tests/media/fixtures/sample-media-sidecars.yaml",
    ),
    (
        ROOT / "schema/jsonschema/media-session-extension.schema.json",
        ROOT / "tests/media/fixtures/sample-media-session-extension.yaml",
    ),
    (
        ROOT / "schema/jsonschema/operator-media-session-view.schema.json",
        ROOT / "tests/media/fixtures/sample-operator-media-session-view.yaml",
    ),
    (
        ROOT / "schema/jsonschema/media-topology-policy.schema.json",
        ROOT / "tests/media/fixtures/sample-media-topology.yaml",
    ),
]
OSS_MANAGED_FIXTURE_SCHEMA_PAIRS = [
    (
        ROOT / "schema/jsonschema/oss-core-manifest.schema.json",
        ROOT / "meta/oss-core-manifest.yaml",
    ),
    (
        ROOT / "schema/jsonschema/managed-surface-catalog.schema.json",
        ROOT / "meta/managed-surface-catalog.yaml",
    ),
    (
        ROOT / "schema/jsonschema/deployment-flavors.schema.json",
        ROOT / "meta/deployment-flavors.yaml",
    ),
    (
        ROOT / "schema/jsonschema/split-release-policy.schema.json",
        ROOT / "meta/split-release-policy.yaml",
    ),
    (
        ROOT / "schema/jsonschema/split-release-manifest.schema.json",
        ROOT / "meta/split-release-manifest.yaml",
    ),
]
ENTERPRISE_FIXTURE_SCHEMA_PAIRS = [
    (
        ROOT / "schema/jsonschema/audit-export-policy.schema.json",
        ROOT / "meta/audit-export-policy.yaml",
    ),
    (
        ROOT / "schema/jsonschema/dedicated-deployment-profile.schema.json",
        ROOT / "meta/dedicated-deployment-profile.yaml",
    ),
    (
        ROOT / "schema/jsonschema/retention-slo-policy.schema.json",
        ROOT / "meta/retention-slo-policy.yaml",
    ),
    (
        ROOT / "schema/jsonschema/enterprise-acceptance-checklist.schema.json",
        ROOT / "meta/enterprise-acceptance-checklist.yaml",
    ),
    (
        ROOT / "schema/jsonschema/enterprise-control-matrix.schema.json",
        ROOT / "meta/enterprise-control-matrix.yaml",
    ),
    (
        ROOT / "schema/jsonschema/dedicated-tenant-evidence.schema.json",
        ROOT / "meta/dedicated-tenant-evidence.yaml",
    ),
]
SIMULATION_FIXTURE_SCHEMA_PAIRS = [
    (
        ROOT / "schema/jsonschema/fault-injection-matrix.schema.json",
        ROOT / "meta/fault-injection-matrix.yaml",
    ),
    (
        ROOT / "schema/jsonschema/simulation-scenario-manifest.schema.json",
        ROOT / "meta/simulation-scenarios.yaml",
    ),
]
SIMULATION_SCENARIO_SCHEMA = ROOT / "schema/jsonschema/simulation-scenario.schema.json"
SIMULATION_SCENARIO_FIXTURES = [
    ROOT / "tests/simulation/fixtures/worker-crash-recovery.yaml",
    ROOT / "tests/simulation/fixtures/node-loss-adoption.yaml",
    ROOT / "tests/simulation/fixtures/approval-timeout.yaml",
    ROOT / "tests/simulation/fixtures/duplicate-callback.yaml",
    ROOT / "tests/simulation/fixtures/browser-instability.yaml",
]
CONFORMANCE_FIXTURE_SCHEMA_PAIRS = [
    (
        ROOT / "schema/jsonschema/conformance-fixture-manifest.schema.json",
        ROOT / "tests/conformance/fixtures/runtime-contract-conformance.yaml",
    ),
    (
        ROOT / "schema/jsonschema/conformance-report.schema.json",
        ROOT / "tests/conformance/fixtures/sample-conformance-report.yaml",
    ),
]
REPLAY_ORACLE_FIXTURE_SCHEMA_PAIRS = [
    (
        ROOT / "schema/jsonschema/determinism-classification.schema.json",
        ROOT / "meta/determinism-classes.yaml",
    ),
    (
        ROOT / "schema/jsonschema/replay-oracle.schema.json",
        ROOT / "meta/replay-equivalence.yaml",
    ),
]
REPLAY_DIFF_FIXTURE_SCHEMA_PAIRS = [
    (
        ROOT / "schema/jsonschema/replay-fixture-manifest.schema.json",
        ROOT / "meta/replay-fixtures.yaml",
    ),
]
PHASE15_FIXTURE_SCHEMA_PAIRS = [
    (
        ROOT / "schema/jsonschema/compatibility-matrix.schema.json",
        ROOT / "meta/compatibility-matrix.yaml",
    ),
    (
        ROOT / "schema/jsonschema/version-skew-rules.schema.json",
        ROOT / "meta/version-skew-rules.yaml",
    ),
    (
        ROOT / "schema/jsonschema/upcaster-manifest.schema.json",
        ROOT / "meta/upcaster-manifests.yaml",
    ),
    (
        ROOT / "schema/jsonschema/upgrade-strategies.schema.json",
        ROOT / "meta/upgrade-strategies.yaml",
    ),
    (
        ROOT / "schema/jsonschema/recovery-objective.schema.json",
        ROOT / "meta/recovery-objectives.yaml",
    ),
    (
        ROOT / "schema/jsonschema/topology-profiles.schema.json",
        ROOT / "meta/topology-profiles.yaml",
    ),
]
PHASE15_ADVANCED_FIXTURE_SCHEMA_PAIRS = [
    (
        ROOT / "schema/jsonschema/upcaster-fixture-manifest.schema.json",
        ROOT / "meta/upcaster-fixtures.yaml",
    ),
    (
        ROOT / "schema/jsonschema/upgrade-drill-manifest.schema.json",
        ROOT / "meta/upgrade-drill-fixtures.yaml",
    ),
    (
        ROOT / "schema/jsonschema/restore-drill-manifest.schema.json",
        ROOT / "meta/restore-drill-fixtures.yaml",
    ),
    (
        ROOT / "schema/jsonschema/standby-promotion-evidence.schema.json",
        ROOT / "meta/standby-promotion-evidence.yaml",
    ),
    (
        ROOT / "schema/jsonschema/release-evidence-manifest.schema.json",
        ROOT / "meta/release-evidence-manifest.yaml",
    ),
]
PHASE16_FIXTURE_SCHEMA_PAIRS = [
    (
        ROOT / "schema/jsonschema/slo-profiles.schema.json",
        ROOT / "meta/slo-profiles.yaml",
    ),
    (
        ROOT / "schema/jsonschema/load-shed-policies.schema.json",
        ROOT / "meta/load-shed-policies.yaml",
    ),
    (
        ROOT / "schema/jsonschema/placement-policies.schema.json",
        ROOT / "meta/placement-policies.yaml",
    ),
    (
        ROOT / "schema/jsonschema/isolation-profiles.schema.json",
        ROOT / "meta/isolation-profiles.yaml",
    ),
    (
        ROOT / "schema/jsonschema/storage-growth-manifest.schema.json",
        ROOT / "meta/storage-growth-fixtures.yaml",
    ),
    (
        ROOT / "schema/jsonschema/fleet-triage-manifest.schema.json",
        ROOT / "meta/fleet-triage-manifest.yaml",
    ),
]
PHASE17_FIXTURE_SCHEMA_PAIRS = [
    (
        ROOT / "schema/jsonschema/regional-topology-profiles.schema.json",
        ROOT / "meta/regional-topology-profiles.yaml",
    ),
    (
        ROOT / "schema/jsonschema/fault-domain-catalog.schema.json",
        ROOT / "meta/fault-domain-catalog.yaml",
    ),
    (
        ROOT / "schema/jsonschema/regional-placement-policies.schema.json",
        ROOT / "meta/regional-placement-policies.yaml",
    ),
    (
        ROOT / "schema/jsonschema/regional-evacuation-manifest.schema.json",
        ROOT / "meta/regional-evacuation-fixtures.yaml",
    ),
    (
        ROOT / "schema/jsonschema/session-mobility-manifest.schema.json",
        ROOT / "meta/session-mobility-manifest.yaml",
    ),
    (
        ROOT / "schema/jsonschema/regional-evidence-manifest.schema.json",
        ROOT / "meta/regional-evidence-manifest.yaml",
    ),
]
PHASE18_FIXTURE_SCHEMA_PAIRS = [
    (
        ROOT / "schema/jsonschema/extension-certification-levels.schema.json",
        ROOT / "meta/extension-certification-levels.yaml",
    ),
    (
        ROOT / "schema/jsonschema/sandbox-profiles.schema.json",
        ROOT / "meta/sandbox-profiles.yaml",
    ),
    (
        ROOT / "schema/jsonschema/policy-bundle-manifest.schema.json",
        ROOT / "meta/policy-bundle-profiles.yaml",
    ),
    (
        ROOT / "schema/jsonschema/public-benchmark-manifest.schema.json",
        ROOT / "meta/public-benchmark-manifest.yaml",
    ),
    (
        ROOT / "schema/jsonschema/ecosystem-evidence-manifest.schema.json",
        ROOT / "meta/ecosystem-evidence-manifest.yaml",
    ),
]
PHASE19_FIXTURE_SCHEMA_PAIRS = [
    (
        ROOT / "schema/jsonschema/adoption-profiles.schema.json",
        ROOT / "meta/adoption-profiles.yaml",
    ),
    (
        ROOT / "schema/jsonschema/reference-deployment-tracks.schema.json",
        ROOT / "meta/reference-deployment-tracks.yaml",
    ),
    (
        ROOT / "schema/jsonschema/operator-exercise-manifest.schema.json",
        ROOT / "meta/operator-exercise-manifest.yaml",
    ),
    (
        ROOT / "schema/jsonschema/golden-path-starter-kits.schema.json",
        ROOT / "meta/golden-path-starter-kits.yaml",
    ),
    (
        ROOT / "schema/jsonschema/adoption-evidence-manifest.schema.json",
        ROOT / "meta/adoption-evidence-manifest.yaml",
    ),
]
PHASE20_FIXTURE_SCHEMA_PAIRS = [
    (
        ROOT / "schema/jsonschema/operator-accreditation.schema.json",
        ROOT / "meta/operator-accreditation.yaml",
    ),
    (
        ROOT / "schema/jsonschema/rollout-wave-manifest.schema.json",
        ROOT / "meta/rollout-wave-manifest.yaml",
    ),
    (
        ROOT / "schema/jsonschema/incident-review-packets.schema.json",
        ROOT / "meta/incident-review-packets.yaml",
    ),
    (
        ROOT / "schema/jsonschema/deprecation-governance.schema.json",
        ROOT / "meta/deprecation-governance.yaml",
    ),
    (
        ROOT / "schema/jsonschema/lifecycle-evidence-manifest.schema.json",
        ROOT / "meta/lifecycle-evidence-manifest.yaml",
    ),
]
BENCHMARK_FIXTURE_SCHEMA_PAIRS = [
    (
        ROOT / "schema/jsonschema/benchmark-corpus.schema.json",
        ROOT / "meta/benchmark-corpus.yaml",
    ),
    (
        ROOT / "schema/jsonschema/performance-budgets.schema.json",
        ROOT / "meta/performance-budgets.yaml",
    ),
]
BENCHMARK_SCORECARD_SCHEMA = ROOT / "schema/jsonschema/benchmark-scorecard.schema.json"
BENCHMARK_SCORECARD = ROOT / "docs/generated/phase-14-benchmark-scorecard.json"
PHASE15_RELEASE_EVIDENCE_SCHEMA = ROOT / "schema/jsonschema/release-evidence-bundle.schema.json"
PHASE15_RELEASE_EVIDENCE = ROOT / "docs/generated/phase-15-release-evidence.json"
PHASE16_FLEET_EVIDENCE_SCHEMA = ROOT / "schema/jsonschema/operator-evidence-bundle.schema.json"
PHASE16_FLEET_EVIDENCE = ROOT / "docs/generated/phase-16-fleet-evidence.json"
PHASE17_REGIONAL_EVIDENCE_SCHEMA = ROOT / "schema/jsonschema/regional-evidence-bundle.schema.json"
PHASE17_REGIONAL_EVIDENCE = ROOT / "docs/generated/phase-17-regional-evidence.json"
PHASE18_ECOSYSTEM_EVIDENCE_SCHEMA = ROOT / "schema/jsonschema/ecosystem-evidence-bundle.schema.json"
PHASE18_ECOSYSTEM_EVIDENCE = ROOT / "docs/generated/phase-18-ecosystem-evidence.json"
PHASE19_ADOPTION_EVIDENCE_SCHEMA = ROOT / "schema/jsonschema/adoption-evidence-bundle.schema.json"
PHASE19_ADOPTION_EVIDENCE = ROOT / "docs/generated/phase-19-adoption-evidence.json"
PHASE20_LIFECYCLE_EVIDENCE_SCHEMA = ROOT / "schema/jsonschema/lifecycle-evidence-bundle.schema.json"
PHASE20_LIFECYCLE_EVIDENCE = ROOT / "docs/generated/phase-20-lifecycle-evidence.json"
PYTHON_VENDOR_ROOT = ROOT / "py" / "vendor"
PYTHON_BINDINGS_ROOT = ROOT / "py" / "packages" / "aegis_contracts_py" / "generated" / "proto"
RUST_BINDINGS_ROOT = ROOT / "rs" / "crates" / "aegis_contracts_rs" / "src" / "generated" / "proto"
BUF_MODE = os.environ.get("AEGIS_BUF_MODE", "auto")
BUF_DOCKER_IMAGE = os.environ.get("AEGIS_BUF_DOCKER_IMAGE", "bufbuild/buf:1.66.0")
BUF_CACHE_DIR = Path(os.environ.get("AEGIS_BUF_CACHE_DIR", str(Path.home() / ".cache" / "aegis-buf")))
MESSAGE_PATTERN = re.compile(r"(?m)^message\s+(\w+)\s*\{")
ENUM_PATTERN = re.compile(r"(?m)^enum\s+(\w+)\s*\{")
PACKAGE_PATTERN = re.compile(r"(?m)^package\s+([^;]+);")


def fail(message: str) -> None:
    print(message)
    sys.exit(1)


def load_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def docker_workspace_path() -> str:
    if shutil.which("cygpath"):
        result = subprocess.run(
            ["cygpath", "-am", str(ROOT)],
            check=True,
            capture_output=True,
            text=True,
        )
        return result.stdout.strip()
    return str(ROOT)


def buf_command(*args: str) -> list[str] | None:
    if BUF_MODE not in {"auto", "local", "docker", "manifest-only"}:
        fail(f"Unsupported AEGIS_BUF_MODE: {BUF_MODE}")

    if BUF_MODE in {"auto", "local"} and shutil.which("buf"):
        return ["buf", *args]

    if BUF_MODE == "local":
        fail("AEGIS_BUF_MODE=local but buf is not installed.")

    if BUF_MODE in {"auto", "docker"} and shutil.which("docker"):
        BUF_CACHE_DIR.mkdir(parents=True, exist_ok=True)
        return [
            "docker",
            "run",
            "--rm",
            "-e",
            "BUF_CACHE_DIR=/root/.cache/buf",
            "-v",
            f"{BUF_CACHE_DIR}:/root/.cache/buf",
            "-v",
            f"{docker_workspace_path()}:/workspace",
            "-w",
            "/workspace",
            BUF_DOCKER_IMAGE,
            *args,
        ]

    if BUF_MODE == "docker":
        fail("AEGIS_BUF_MODE=docker but docker is not available.")

    return None


def run_buf(*args: str) -> bool:
    command = buf_command(*args)
    if command is None:
        return False

    subprocess.run(command, cwd=ROOT, check=True)
    return True


def contract_source_digest() -> str:
    digest = hashlib.sha256()
    paths = [
        ROOT / "buf.yaml",
        ROOT / "buf.gen.yaml",
        ROOT / "schema/transport-topology.yaml",
        *sorted(PROTO_ROOT.rglob("*.proto")),
    ]

    for path in paths:
        digest.update(path.relative_to(ROOT).as_posix().encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")

    return digest.hexdigest()


def tool_registry_source_digest() -> str:
    digest = hashlib.sha256()
    digest.update(TOOL_REGISTRY_ROOT.relative_to(ROOT).as_posix().encode("utf-8"))
    digest.update(b"\0")
    digest.update(TOOL_REGISTRY_ROOT.read_bytes())
    digest.update(b"\0")
    return digest.hexdigest()


def dangerous_actions_source_digest() -> str:
    digest = hashlib.sha256()
    digest.update(DANGEROUS_ACTIONS_ROOT.relative_to(ROOT).as_posix().encode("utf-8"))
    digest.update(b"\0")
    digest.update(DANGEROUS_ACTIONS_ROOT.read_bytes())
    digest.update(b"\0")
    return digest.hexdigest()


def dangerous_action_source_digest() -> str:
    digest = hashlib.sha256()
    digest.update(DANGEROUS_ACTION_ROOT.relative_to(ROOT).as_posix().encode("utf-8"))
    digest.update(b"\0")
    digest.update(DANGEROUS_ACTION_ROOT.read_bytes())
    digest.update(b"\0")
    return digest.hexdigest()


def rbac_roles_source_digest() -> str:
    digest = hashlib.sha256()
    digest.update(RBAC_ROLES_ROOT.relative_to(ROOT).as_posix().encode("utf-8"))
    digest.update(b"\0")
    digest.update(RBAC_ROLES_ROOT.read_bytes())
    digest.update(b"\0")
    return digest.hexdigest()


def abac_attributes_source_digest() -> str:
    digest = hashlib.sha256()
    digest.update(ABAC_ATTRIBUTES_ROOT.relative_to(ROOT).as_posix().encode("utf-8"))
    digest.update(b"\0")
    digest.update(ABAC_ATTRIBUTES_ROOT.read_bytes())
    digest.update(b"\0")
    return digest.hexdigest()


def proto_inventory() -> list[dict[str, object]]:
    inventory: list[dict[str, object]] = []
    for proto_file in sorted(PROTO_ROOT.rglob("*.proto")):
        text = proto_file.read_text(encoding="utf-8")
        package_match = PACKAGE_PATTERN.search(text)
        if package_match is None:
            fail(f"Proto missing package statement: {proto_file.relative_to(ROOT)}")

        inventory.append(
            {
                "path": proto_file,
                "relative": proto_file.relative_to(PROTO_ROOT),
                "package": package_match.group(1),
                "messages": sorted(set(MESSAGE_PATTERN.findall(text))),
                "enums": sorted(set(ENUM_PATTERN.findall(text))),
            }
        )

    return inventory


def load_python_module(module_path: Path):
    original_sys_path = list(sys.path)
    # Validate generated bindings against the repo-local runtime, not ambient
    # global site-packages, so contract checks stay hermetic.
    sys.path.insert(0, str(PYTHON_VENDOR_ROOT))
    sys.path.insert(1, str(PYTHON_BINDINGS_ROOT))
    try:
        spec = importlib.util.spec_from_file_location(
            f"aegis_generated_{module_path.stem}",
            module_path,
        )
        if spec is None or spec.loader is None:
            fail(f"Unable to import generated Python bindings: {module_path.relative_to(ROOT)}")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    finally:
        sys.path[:] = original_sys_path


def validate_generated_python_bindings(proto_defs: list[dict[str, object]], digest: str) -> None:
    marker = PYTHON_BINDINGS_ROOT / ".source_digest"
    if not marker.exists():
        fail(f"Missing generated Python bindings digest marker: {marker.relative_to(ROOT)}")
    if marker.read_text(encoding="utf-8").strip() != digest:
        fail(f"Stale generated Python bindings marker: {marker.relative_to(ROOT)}")

    expected_modules: set[Path] = set()
    for proto_def in proto_defs:
        relative = proto_def["relative"]
        if not isinstance(relative, Path):
            fail("Proto inventory corruption for generated Python bindings.")

        module_path = PYTHON_BINDINGS_ROOT / relative.with_name(f"{relative.stem}_pb2.py")
        expected_modules.add(module_path)
        if not module_path.exists():
            fail(f"Missing generated Python bindings: {module_path.relative_to(ROOT)}")

        module = load_python_module(module_path)
        package = str(proto_def["package"])
        for message in proto_def["messages"]:
            descriptor = getattr(getattr(module, str(message), None), "DESCRIPTOR", None)
            if descriptor is None or descriptor.full_name != f"{package}.{message}":
                fail(
                    "Generated Python bindings are missing message "
                    f"{package}.{message} in {module_path.relative_to(ROOT)}"
                )
        for enum in proto_def["enums"]:
            descriptor = getattr(getattr(module, str(enum), None), "DESCRIPTOR", None)
            if descriptor is None or descriptor.full_name != f"{package}.{enum}":
                fail(
                    "Generated Python bindings are missing enum "
                    f"{package}.{enum} in {module_path.relative_to(ROOT)}"
                )

    actual_modules = set(PYTHON_BINDINGS_ROOT.rglob("*_pb2.py"))
    if actual_modules != expected_modules:
        unexpected = sorted(path.relative_to(ROOT).as_posix() for path in actual_modules - expected_modules)
        missing = sorted(path.relative_to(ROOT).as_posix() for path in expected_modules - actual_modules)
        fail(
            "Generated Python bindings do not match the canonical proto set: "
            f"missing={missing} unexpected={unexpected}"
        )


def validate_generated_rust_bindings(proto_defs: list[dict[str, object]], digest: str) -> None:
    rust_sources = sorted(RUST_BINDINGS_ROOT.rglob("*.rs"))
    if not rust_sources:
        return

    marker = RUST_BINDINGS_ROOT / ".source_digest"
    if not marker.exists():
        fail(f"Missing generated Rust bindings digest marker: {marker.relative_to(ROOT)}")
    if marker.read_text(encoding="utf-8").strip() != digest:
        fail(f"Stale generated Rust bindings marker: {marker.relative_to(ROOT)}")

    rust_text = "\n".join(path.read_text(encoding="utf-8") for path in rust_sources)
    for proto_def in proto_defs:
        for message in proto_def["messages"]:
            if f"pub struct {message}" not in rust_text:
                fail(f"Generated Rust bindings are missing struct {message}")
        for enum in proto_def["enums"]:
            if f"pub enum {enum}" not in rust_text:
                fail(f"Generated Rust bindings are missing enum {enum}")


def validate_tool_registry() -> None:
    registry = yaml.safe_load(TOOL_REGISTRY_ROOT.read_text(encoding="utf-8"))
    tool_schema = load_json(ROOT / "schema/jsonschema/tool-descriptor.schema.json")
    dangerous_actions = yaml.safe_load(DANGEROUS_ACTION_ROOT.read_text(encoding="utf-8"))
    dangerous_ids = {item["id"] for item in dangerous_actions["dangerous_action_classes"]}

    if registry.get("registry_version") != 1:
        fail("schema/tool-registry.yaml must declare registry_version: 1")

    tools = registry.get("tools")
    if not isinstance(tools, list) or not tools:
        fail("schema/tool-registry.yaml must define a non-empty tools list")

    seen_tool_ids: set[str] = set()
    for descriptor in tools:
        validate(instance=descriptor, schema=tool_schema)

        tool_id = descriptor["tool_id"]
        if tool_id in seen_tool_ids:
            fail(f"Duplicate tool descriptor: {tool_id}")
        seen_tool_ids.add(tool_id)

        for schema_ref_key in ("input_schema_ref", "output_schema_ref"):
            schema_ref = ROOT / descriptor[schema_ref_key]
            if not schema_ref.exists():
                fail(
                    "Tool descriptor "
                    f"{tool_id} references missing schema {descriptor[schema_ref_key]}"
                )

        dangerous_action_class = descriptor.get("dangerous_action_class")
        if dangerous_action_class is not None and dangerous_action_class not in dangerous_ids:
            fail(
                "Tool descriptor "
                f"{tool_id} references unknown dangerous action class {dangerous_action_class}"
            )

    digest = tool_registry_source_digest()
    if not TOOL_REGISTRY_GENERATED_TARGET.exists():
        fail(
            "Missing generated tool registry manifest: "
            f"{TOOL_REGISTRY_GENERATED_TARGET.relative_to(ROOT)}"
        )
    if f'@source_digest "{digest}"' not in TOOL_REGISTRY_GENERATED_TARGET.read_text(encoding="utf-8"):
        fail(
            "Stale generated tool registry manifest: "
            f"{TOOL_REGISTRY_GENERATED_TARGET.relative_to(ROOT)}"
        )

    dangerous_digest = dangerous_actions_source_digest()
    if not DANGEROUS_ACTIONS_GENERATED_TARGET.exists():
        fail(
            "Missing generated dangerous-action catalog manifest: "
            f"{DANGEROUS_ACTIONS_GENERATED_TARGET.relative_to(ROOT)}"
        )
    if f'@source_digest "{dangerous_digest}"' not in DANGEROUS_ACTIONS_GENERATED_TARGET.read_text(encoding="utf-8"):
        fail(
            "Stale generated dangerous-action catalog manifest: "
            f"{DANGEROUS_ACTIONS_GENERATED_TARGET.relative_to(ROOT)}"
        )

    dangerous_digest = dangerous_action_source_digest()
    if not DANGEROUS_ACTION_GENERATED_TARGET.exists():
        fail(
            "Missing generated dangerous-action catalog manifest: "
            f"{DANGEROUS_ACTION_GENERATED_TARGET.relative_to(ROOT)}"
        )
    if (
        f'@source_digest "{dangerous_digest}"'
        not in DANGEROUS_ACTION_GENERATED_TARGET.read_text(encoding="utf-8")
    ):
        fail(
            "Stale generated dangerous-action catalog manifest: "
            f"{DANGEROUS_ACTION_GENERATED_TARGET.relative_to(ROOT)}"
        )

    rbac_digest = rbac_roles_source_digest()
    if not RBAC_ROLES_GENERATED_TARGET.exists():
        fail(
            "Missing generated RBAC catalog manifest: "
            f"{RBAC_ROLES_GENERATED_TARGET.relative_to(ROOT)}"
        )
    if f'@source_digest "{rbac_digest}"' not in RBAC_ROLES_GENERATED_TARGET.read_text(encoding="utf-8"):
        fail(
            "Stale generated RBAC catalog manifest: "
            f"{RBAC_ROLES_GENERATED_TARGET.relative_to(ROOT)}"
        )

    abac_digest = abac_attributes_source_digest()
    if not ABAC_ATTRIBUTES_GENERATED_TARGET.exists():
        fail(
            "Missing generated ABAC catalog manifest: "
            f"{ABAC_ATTRIBUTES_GENERATED_TARGET.relative_to(ROOT)}"
        )
    if f'@source_digest "{abac_digest}"' not in ABAC_ATTRIBUTES_GENERATED_TARGET.read_text(encoding="utf-8"):
        fail(
            "Stale generated ABAC catalog manifest: "
            f"{ABAC_ATTRIBUTES_GENERATED_TARGET.relative_to(ROOT)}"
        )


def validate_extension_manifests() -> None:
    schema = load_json(EXTENSION_MANIFEST_SCHEMA)

    for fixture in EXTENSION_MANIFEST_FIXTURES:
        payload = yaml.safe_load(fixture.read_text(encoding="utf-8"))
        try:
            validate(instance=payload, schema=schema)
        except Exception as exc:  # pragma: no cover - exits immediately
            fail(f"Invalid extension manifest fixture {fixture.relative_to(ROOT)}: {exc}")


def validate_extension_compatibility_policy() -> None:
    schema = load_json(EXTENSION_COMPATIBILITY_POLICY_SCHEMA)
    payload = yaml.safe_load(EXTENSION_COMPATIBILITY_POLICY.read_text(encoding="utf-8"))
    try:
        validate(instance=payload, schema=schema)
    except Exception as exc:  # pragma: no cover - exits immediately
        fail(
            "Invalid extension compatibility policy fixture "
            f"{EXTENSION_COMPATIBILITY_POLICY.relative_to(ROOT)}: {exc}"
        )


def validate_extension_pack() -> None:
    pack_schema = load_json(EXTENSION_PACK_MANIFEST_SCHEMA)
    extension_schema = load_json(EXTENSION_MANIFEST_SCHEMA)
    pack = yaml.safe_load(EXTENSION_PACK_MANIFEST.read_text(encoding="utf-8"))
    pack_root = EXTENSION_PACK_MANIFEST.parent

    try:
        validate(instance=pack, schema=pack_schema)
    except Exception as exc:  # pragma: no cover - exits immediately
        fail(f"Invalid extension pack manifest {EXTENSION_PACK_MANIFEST.relative_to(ROOT)}: {exc}")

    for ref_key in ("compatibility_policy_ref", "review_rubric_ref", "readme_ref"):
        resolved = (pack_root / pack[ref_key]).resolve()
        if not resolved.exists():
            fail(
                "Extension pack manifest references missing file "
                f"{Path(resolved).relative_to(ROOT)}"
            )

    for directory_key in ("connectors_dir", "artifact_processors_dir", "mcp_adapters_dir"):
        resolved = (pack_root / pack["layout"][directory_key]).resolve()
        if not resolved.is_dir():
            fail(
                "Extension pack layout references missing directory "
                f"{Path(resolved).relative_to(ROOT)}"
            )

    for member in pack["members"]:
        manifest_path = (pack_root / member["manifest_ref"]).resolve()
        if not manifest_path.exists():
            fail(
                "Extension pack member references missing manifest "
                f"{Path(manifest_path).relative_to(ROOT)}"
            )
        payload = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
        try:
            validate(instance=payload, schema=extension_schema)
        except Exception as exc:  # pragma: no cover - exits immediately
            fail(f"Invalid extension pack member {Path(manifest_path).relative_to(ROOT)}: {exc}")


def validate_media_fixtures() -> None:
    for schema_path, fixture_path in MEDIA_FIXTURE_SCHEMA_PAIRS:
        schema = load_json(schema_path)
        payload = yaml.safe_load(fixture_path.read_text(encoding="utf-8"))
        try:
            validate(instance=payload, schema=schema)
        except Exception as exc:  # pragma: no cover - exits immediately
            fail(
                "Invalid media fixture "
                f"{fixture_path.relative_to(ROOT)} for schema {schema_path.relative_to(ROOT)}: {exc}"
            )


def validate_oss_managed_artifacts() -> None:
    for schema_path, fixture_path in OSS_MANAGED_FIXTURE_SCHEMA_PAIRS:
        schema = load_json(schema_path)
        payload = yaml.safe_load(fixture_path.read_text(encoding="utf-8"))
        try:
            validate(instance=payload, schema=schema)
        except Exception as exc:  # pragma: no cover - exits immediately
            fail(
                "Invalid OSS/managed split artifact "
                f"{fixture_path.relative_to(ROOT)} for schema {schema_path.relative_to(ROOT)}: {exc}"
            )


def validate_enterprise_artifacts() -> None:
    for schema_path, fixture_path in ENTERPRISE_FIXTURE_SCHEMA_PAIRS:
        schema = load_json(schema_path)
        payload = yaml.safe_load(fixture_path.read_text(encoding="utf-8"))
        try:
            validate(instance=payload, schema=schema)
        except Exception as exc:  # pragma: no cover - exits immediately
            fail(
                "Invalid enterprise artifact "
                f"{fixture_path.relative_to(ROOT)} for schema {schema_path.relative_to(ROOT)}: {exc}"
            )


def validate_replay_oracle_artifacts() -> None:
    for schema_path, fixture_path in REPLAY_ORACLE_FIXTURE_SCHEMA_PAIRS:
        schema = load_json(schema_path)
        payload = yaml.safe_load(fixture_path.read_text(encoding="utf-8"))
        try:
            validate(instance=payload, schema=schema)
        except Exception as exc:  # pragma: no cover - exits immediately
            fail(
                "Invalid replay-oracle artifact "
                f"{fixture_path.relative_to(ROOT)} for schema {schema_path.relative_to(ROOT)}: {exc}"
            )


def validate_simulation_artifacts() -> None:
    for schema_path, fixture_path in SIMULATION_FIXTURE_SCHEMA_PAIRS:
        schema = load_json(schema_path)
        payload = yaml.safe_load(fixture_path.read_text(encoding="utf-8"))
        try:
            validate(instance=payload, schema=schema)
        except Exception as exc:  # pragma: no cover - exits immediately
            fail(
                "Invalid simulation artifact "
                f"{fixture_path.relative_to(ROOT)} for schema {schema_path.relative_to(ROOT)}: {exc}"
            )

    scenario_schema = load_json(SIMULATION_SCENARIO_SCHEMA)
    for fixture_path in SIMULATION_SCENARIO_FIXTURES:
        payload = yaml.safe_load(fixture_path.read_text(encoding="utf-8"))
        try:
            validate(instance=payload, schema=scenario_schema)
        except Exception as exc:  # pragma: no cover - exits immediately
            fail(
                "Invalid simulation scenario "
                f"{fixture_path.relative_to(ROOT)} for schema {SIMULATION_SCENARIO_SCHEMA.relative_to(ROOT)}: {exc}"
            )


def validate_conformance_artifacts() -> None:
    for schema_path, fixture_path in CONFORMANCE_FIXTURE_SCHEMA_PAIRS:
        schema = load_json(schema_path)
        payload = yaml.safe_load(fixture_path.read_text(encoding="utf-8"))
        try:
            validate(instance=payload, schema=schema)
        except Exception as exc:  # pragma: no cover - exits immediately
            fail(
                "Invalid conformance artifact "
                f"{fixture_path.relative_to(ROOT)} for schema {schema_path.relative_to(ROOT)}: {exc}"
            )


def validate_replay_diff_artifacts() -> None:
    for schema_path, fixture_path in REPLAY_DIFF_FIXTURE_SCHEMA_PAIRS:
        schema = load_json(schema_path)
        payload = yaml.safe_load(fixture_path.read_text(encoding="utf-8"))
        try:
            validate(instance=payload, schema=schema)
        except Exception as exc:  # pragma: no cover - exits immediately
            fail(
                "Invalid replay-diff artifact "
                f"{fixture_path.relative_to(ROOT)} for schema {schema_path.relative_to(ROOT)}: {exc}"
            )


def validate_phase15_artifacts() -> None:
    for schema_path, fixture_path in PHASE15_FIXTURE_SCHEMA_PAIRS:
        schema = load_json(schema_path)
        payload = yaml.safe_load(fixture_path.read_text(encoding="utf-8"))
        try:
            validate(instance=payload, schema=schema)
        except Exception as exc:  # pragma: no cover - exits immediately
            fail(
                "Invalid phase-15 artifact "
                f"{fixture_path.relative_to(ROOT)} for schema {schema_path.relative_to(ROOT)}: {exc}"
            )

    for schema_path, fixture_path in PHASE15_ADVANCED_FIXTURE_SCHEMA_PAIRS:
        schema = load_json(schema_path)
        payload = yaml.safe_load(fixture_path.read_text(encoding="utf-8"))
        try:
            validate(instance=payload, schema=schema)
        except Exception as exc:  # pragma: no cover - exits immediately
            fail(
                "Invalid phase-15 advanced artifact "
                f"{fixture_path.relative_to(ROOT)} for schema {schema_path.relative_to(ROOT)}: {exc}"
            )

    release_schema = load_json(PHASE15_RELEASE_EVIDENCE_SCHEMA)
    release_bundle = load_json(PHASE15_RELEASE_EVIDENCE)
    try:
        validate(instance=release_bundle, schema=release_schema)
    except Exception as exc:  # pragma: no cover - exits immediately
        fail(
            "Invalid phase-15 release evidence "
            f"{PHASE15_RELEASE_EVIDENCE.relative_to(ROOT)} for schema {PHASE15_RELEASE_EVIDENCE_SCHEMA.relative_to(ROOT)}: {exc}"
        )


def validate_phase16_artifacts() -> None:
    for schema_path, fixture_path in PHASE16_FIXTURE_SCHEMA_PAIRS:
        schema = load_json(schema_path)
        payload = yaml.safe_load(fixture_path.read_text(encoding="utf-8"))
        try:
            validate(instance=payload, schema=schema)
        except Exception as exc:  # pragma: no cover - exits immediately
            fail(
                "Invalid phase-16 artifact "
                f"{fixture_path.relative_to(ROOT)} for schema {schema_path.relative_to(ROOT)}: {exc}"
            )

    fleet_schema = load_json(PHASE16_FLEET_EVIDENCE_SCHEMA)
    fleet_bundle = load_json(PHASE16_FLEET_EVIDENCE)
    try:
        validate(instance=fleet_bundle, schema=fleet_schema)
    except Exception as exc:  # pragma: no cover - exits immediately
        fail(
            "Invalid phase-16 fleet evidence "
            f"{PHASE16_FLEET_EVIDENCE.relative_to(ROOT)} for schema {PHASE16_FLEET_EVIDENCE_SCHEMA.relative_to(ROOT)}: {exc}"
        )


def validate_phase17_artifacts() -> None:
    for schema_path, fixture_path in PHASE17_FIXTURE_SCHEMA_PAIRS:
        schema = load_json(schema_path)
        payload = yaml.safe_load(fixture_path.read_text(encoding="utf-8"))
        try:
            validate(instance=payload, schema=schema)
        except Exception as exc:  # pragma: no cover - exits immediately
            fail(
                "Invalid phase-17 artifact "
                f"{fixture_path.relative_to(ROOT)} for schema {schema_path.relative_to(ROOT)}: {exc}"
            )

    regional_schema = load_json(PHASE17_REGIONAL_EVIDENCE_SCHEMA)
    regional_bundle = load_json(PHASE17_REGIONAL_EVIDENCE)
    try:
        validate(instance=regional_bundle, schema=regional_schema)
    except Exception as exc:  # pragma: no cover - exits immediately
        fail(
            "Invalid phase-17 regional evidence "
            f"{PHASE17_REGIONAL_EVIDENCE.relative_to(ROOT)} for schema {PHASE17_REGIONAL_EVIDENCE_SCHEMA.relative_to(ROOT)}: {exc}"
        )


def validate_phase18_artifacts() -> None:
    for schema_path, fixture_path in PHASE18_FIXTURE_SCHEMA_PAIRS:
        schema = load_json(schema_path)
        payload = yaml.safe_load(fixture_path.read_text(encoding="utf-8"))
        try:
            validate(instance=payload, schema=schema)
        except Exception as exc:  # pragma: no cover - exits immediately
            fail(
                "Invalid phase-18 artifact "
                f"{fixture_path.relative_to(ROOT)} for schema {schema_path.relative_to(ROOT)}: {exc}"
            )

    ecosystem_schema = load_json(PHASE18_ECOSYSTEM_EVIDENCE_SCHEMA)
    ecosystem_bundle = load_json(PHASE18_ECOSYSTEM_EVIDENCE)
    try:
        validate(instance=ecosystem_bundle, schema=ecosystem_schema)
    except Exception as exc:  # pragma: no cover - exits immediately
        fail(
            "Invalid phase-18 ecosystem evidence "
            f"{PHASE18_ECOSYSTEM_EVIDENCE.relative_to(ROOT)} for schema {PHASE18_ECOSYSTEM_EVIDENCE_SCHEMA.relative_to(ROOT)}: {exc}"
        )


def validate_phase19_artifacts() -> None:
    for schema_path, fixture_path in PHASE19_FIXTURE_SCHEMA_PAIRS:
        schema = load_json(schema_path)
        payload = yaml.safe_load(fixture_path.read_text(encoding="utf-8"))
        try:
            validate(instance=payload, schema=schema)
        except Exception as exc:  # pragma: no cover - exits immediately
            fail(
                "Invalid phase-19 artifact "
                f"{fixture_path.relative_to(ROOT)} for schema {schema_path.relative_to(ROOT)}: {exc}"
            )

    adoption_schema = load_json(PHASE19_ADOPTION_EVIDENCE_SCHEMA)
    adoption_bundle = load_json(PHASE19_ADOPTION_EVIDENCE)
    try:
        validate(instance=adoption_bundle, schema=adoption_schema)
    except Exception as exc:  # pragma: no cover - exits immediately
        fail(
            "Invalid phase-19 adoption evidence "
            f"{PHASE19_ADOPTION_EVIDENCE.relative_to(ROOT)} for schema {PHASE19_ADOPTION_EVIDENCE_SCHEMA.relative_to(ROOT)}: {exc}"
        )


def validate_phase20_artifacts() -> None:
    for schema_path, fixture_path in PHASE20_FIXTURE_SCHEMA_PAIRS:
        schema = load_json(schema_path)
        payload = yaml.safe_load(fixture_path.read_text(encoding="utf-8"))
        try:
            validate(instance=payload, schema=schema)
        except Exception as exc:  # pragma: no cover - exits immediately
            fail(
                "Invalid phase-20 artifact "
                f"{fixture_path.relative_to(ROOT)} for schema {schema_path.relative_to(ROOT)}: {exc}"
            )

    lifecycle_schema = load_json(PHASE20_LIFECYCLE_EVIDENCE_SCHEMA)
    lifecycle_bundle = load_json(PHASE20_LIFECYCLE_EVIDENCE)
    try:
        validate(instance=lifecycle_bundle, schema=lifecycle_schema)
    except Exception as exc:  # pragma: no cover - exits immediately
        fail(
            "Invalid phase-20 lifecycle evidence "
            f"{PHASE20_LIFECYCLE_EVIDENCE.relative_to(ROOT)} for schema {PHASE20_LIFECYCLE_EVIDENCE_SCHEMA.relative_to(ROOT)}: {exc}"
        )


def validate_benchmark_artifacts() -> None:
    for schema_path, fixture_path in BENCHMARK_FIXTURE_SCHEMA_PAIRS:
        schema = load_json(schema_path)
        payload = yaml.safe_load(fixture_path.read_text(encoding="utf-8"))
        try:
            validate(instance=payload, schema=schema)
        except Exception as exc:  # pragma: no cover - exits immediately
            fail(
                "Invalid benchmark artifact "
                f"{fixture_path.relative_to(ROOT)} for schema {schema_path.relative_to(ROOT)}: {exc}"
            )

    scorecard_schema = load_json(BENCHMARK_SCORECARD_SCHEMA)
    scorecard = load_json(BENCHMARK_SCORECARD)
    try:
        validate(instance=scorecard, schema=scorecard_schema)
    except Exception as exc:  # pragma: no cover - exits immediately
        fail(
            "Invalid benchmark scorecard "
            f"{BENCHMARK_SCORECARD.relative_to(ROOT)} for schema {BENCHMARK_SCORECARD_SCHEMA.relative_to(ROOT)}: {exc}"
        )


schema_dirs = [
    ROOT / "schema/jsonschema",
    ROOT / "schema/event-payloads",
    ROOT / "schema/checkpoints",
]
for schema_dir in schema_dirs:
    for schema_file in schema_dir.glob("*.json"):
        try:
            schema = load_json(schema_file)
            cls = validator_for(schema)
            cls.check_schema(schema)
        except Exception as exc:  # pragma: no cover - exits immediately
            fail(f"Invalid JSON schema {schema_file.relative_to(ROOT)}: {exc}")


catalog = yaml.safe_load((ROOT / "schema/event-catalog/events.yaml").read_text(encoding="utf-8"))
index = yaml.safe_load((ROOT / "schema/event-catalog/index.yaml").read_text(encoding="utf-8"))
events = catalog.get("events", [])
index_map = {event["type"]: event for event in index.get("events", [])}
seen = set()
for event in events:
    for key in ["type", "category", "determinism", "description", "required_payload", "version", "schema_ref"]:
        if key not in event:
            fail(f"Event {event.get('type')} missing key {key}")
    if event["type"] in seen:
        fail(f"Duplicate event type: {event['type']}")
    seen.add(event["type"])
    schema_ref = ROOT / event["schema_ref"]
    if not schema_ref.exists():
        fail(f"Event {event['type']} references missing schema {event['schema_ref']}")
    if event["type"] not in index_map:
        fail(f"Event {event['type']} missing from index.yaml")
    if index_map[event["type"]]["schema_ref"] != event["schema_ref"] or index_map[event["type"]]["version"] != event["version"]:
        fail(f"Event index mismatch for {event['type']}")


transport = yaml.safe_load((ROOT / "schema/transport-topology.yaml").read_text(encoding="utf-8"))
transport_schema = load_json(ROOT / "schema/jsonschema/transport-topology.schema.json")
validate(instance=transport, schema=transport_schema)

proto_defs = proto_inventory()
message_names = {
    str(message)
    for proto_def in proto_defs
    for message in proto_def["messages"]
}
if not message_names:
    fail("No proto messages found.")

subject_map = {subject["name"]: subject for subject in transport["subjects"]}
stream_subject_patterns = []
for stream in transport["streams"]:
    stream_subject_patterns.extend(stream["subjects"])

for subject in transport["subjects"]:
    if subject["message"] not in message_names:
        fail(
            "Transport subject "
            f"{subject['name']} points to missing proto message {subject['message']}"
        )


def normalize(pattern: str) -> str:
    return pattern.replace("{worker_kind}", "*")


mapped_subjects = [normalize(subject["subject"]) for subject in transport["subjects"]]
for stream_pattern in stream_subject_patterns:
    matched = any(
        stream_pattern == mapped_subject
        or (stream_pattern.endswith(">") and mapped_subject.startswith(stream_pattern[:-1]))
        or (mapped_subject.endswith("*") and stream_pattern.startswith(mapped_subject[:-1]))
        or (stream_pattern.endswith("*") and mapped_subject.startswith(stream_pattern[:-1]))
        for mapped_subject in mapped_subjects
    )
    if not matched:
        fail(f"Stream subject pattern has no mapped subject entry: {stream_pattern}")


cancel_consumers = [
    consumer
    for consumer in transport["consumers"]
    if ".command.cancel." in consumer["filter_subject"]
]
dispatch_consumers = [
    consumer
    for consumer in transport["consumers"]
    if ".command.dispatch." in consumer["filter_subject"]
]
if not cancel_consumers:
    fail("transport-topology.yaml must define explicit cancel consumers")
worker_kinds = {consumer["filter_subject"].split(".")[-1] for consumer in dispatch_consumers}
cancel_kinds = {consumer["filter_subject"].split(".")[-1] for consumer in cancel_consumers}
if worker_kinds != cancel_kinds:
    fail(
        "Cancel consumers do not cover same worker kinds as dispatch consumers: "
        f"dispatch={sorted(worker_kinds)} cancel={sorted(cancel_kinds)}"
    )


for proto_def in proto_defs:
    text = proto_def["path"].read_text(encoding="utf-8")
    if "package " not in text:
        fail(f"Proto missing package statement: {proto_def['path'].relative_to(ROOT)}")


if run_buf("lint"):
    pass
else:
    print("buf not installed and docker unavailable; falling back to structural proto validation.")


digest = contract_source_digest()
generated_targets = {
    ROOT / "apps/aegis_execution_bridge/lib/aegis/execution_bridge/generated/contracts.ex": f'@source_digest "{digest}"',
    ROOT / "py/packages/aegis_contracts_py/generated/manifest.py": f"SOURCE_DIGEST = '{digest}'",
    ROOT / "rs/crates/aegis_contracts_rs/src/generated/mod.rs": f'pub const SOURCE_DIGEST: &str = "{digest}";',
}

for target, marker in generated_targets.items():
    if not target.exists():
        fail(f"Missing generated contract manifest: {target.relative_to(ROOT)}")
    if marker not in target.read_text(encoding="utf-8"):
        fail(f"Stale generated contract manifest: {target.relative_to(ROOT)}")


validate_generated_python_bindings(proto_defs, digest)
validate_generated_rust_bindings(proto_defs, digest)
validate_tool_registry()
validate_extension_manifests()
validate_extension_compatibility_policy()
validate_extension_pack()
validate_media_fixtures()
validate_oss_managed_artifacts()
validate_enterprise_artifacts()
validate_replay_oracle_artifacts()
validate_simulation_artifacts()
validate_conformance_artifacts()
validate_replay_diff_artifacts()
validate_phase15_artifacts()
validate_phase16_artifacts()
validate_phase17_artifacts()
validate_phase18_artifacts()
validate_phase19_artifacts()
validate_phase20_artifacts()
validate_benchmark_artifacts()

if subject_map["dispatch"]["message"] != "ActionDispatch":
    fail("Transport subject mapping for dispatch drifted from ActionDispatch")
if subject_map["cancelled"]["message"] != "ActionCancelled":
    fail("Transport subject mapping for cancelled drifted from ActionCancelled")

print("Schema validation passed.")
