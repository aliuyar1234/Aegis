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

if subject_map["dispatch"]["message"] != "ActionDispatch":
    fail("Transport subject mapping for dispatch drifted from ActionDispatch")
if subject_map["cancelled"]["message"] != "ActionCancelled":
    fail("Transport subject mapping for cancelled drifted from ActionCancelled")

print("Schema validation passed.")
