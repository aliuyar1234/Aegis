#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
PROTO_ROOT = ROOT / "schema" / "proto"
TOPOLOGY_PATH = ROOT / "schema" / "transport-topology.yaml"
BUF_FILES = [ROOT / "buf.yaml", ROOT / "buf.gen.yaml"]
PROTO_PATTERN = re.compile(r"(?ms)^message\s+(\w+)\s*\{.*?^\}")
ENUM_PATTERN = re.compile(r"(?ms)^enum\s+(\w+)\s*\{.*?^\}")
PACKAGE_PATTERN = re.compile(r"(?m)^package\s+([^;]+);")


def main() -> None:
    manifest = build_manifest()
    write_elixir_manifest(manifest)
    write_python_manifest(manifest)
    write_rust_manifest(manifest)


def build_manifest() -> dict[str, object]:
    proto_files = sorted(PROTO_ROOT.rglob("*.proto"))
    packages: dict[str, dict[str, list[str]]] = {}

    for proto_file in proto_files:
        text = proto_file.read_text(encoding="utf-8")
        package_match = PACKAGE_PATTERN.search(text)
        if package_match is None:
            raise ValueError(f"Missing package statement in {proto_file}")

        package = package_match.group(1)
        package_entry = packages.setdefault(package, {"messages": [], "enums": []})
        package_entry["messages"].extend(sorted(PROTO_PATTERN.findall(text)))
        package_entry["enums"].extend(sorted(ENUM_PATTERN.findall(text)))

    for package, entry in packages.items():
        entry["messages"] = sorted(set(entry["messages"]))
        entry["enums"] = sorted(set(entry["enums"]))

    topology = yaml.safe_load(TOPOLOGY_PATH.read_text(encoding="utf-8"))
    source_files = BUF_FILES + [TOPOLOGY_PATH] + proto_files

    return {
        "source_digest": source_digest(source_files),
        "source_files": [path.relative_to(ROOT).as_posix() for path in source_files],
        "packages": packages,
        "message_names": sorted(
            {
                message
                for package in packages.values()
                for message in package["messages"]
            }
        ),
        "enum_names": sorted(
            {
                enum
                for package in packages.values()
                for enum in package["enums"]
            }
        ),
        "transport_topology": topology,
    }


def source_digest(paths: list[Path]) -> str:
    digest = hashlib.sha256()
    for path in paths:
        digest.update(path.relative_to(ROOT).as_posix().encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def write_elixir_manifest(manifest: dict[str, object]) -> None:
    target = (
        ROOT
        / "apps"
        / "aegis_execution_bridge"
        / "lib"
        / "aegis"
        / "execution_bridge"
        / "generated"
        / "contracts.ex"
    )
    ensure_parent(target)

    body = f"""defmodule Aegis.ExecutionBridge.Generated.Contracts do
  @moduledoc false

  @source_digest "{manifest["source_digest"]}"
  @source_files {to_elixir(manifest["source_files"])}
  @packages {to_elixir(manifest["packages"])}
  @message_names {to_elixir(manifest["message_names"])}
  @enum_names {to_elixir(manifest["enum_names"])}
  @transport_topology {to_elixir(manifest["transport_topology"])}

  def source_digest, do: @source_digest
  def source_files, do: @source_files
  def packages, do: @packages
  def message_names, do: @message_names
  def enum_names, do: @enum_names
  def transport_topology, do: @transport_topology
end
"""
    target.write_text(body, encoding="utf-8")


def write_python_manifest(manifest: dict[str, object]) -> None:
    package_root = ROOT / "py" / "packages" / "aegis_contracts_py" / "generated"
    ensure_parent(package_root / "__init__.py")

    manifest_text = f"""\"\"\"Generated from schema/proto and schema/transport-topology.yaml.\"\"\"

SOURCE_DIGEST = {manifest["source_digest"]!r}
SOURCE_FILES = {python_repr(manifest["source_files"])}
PACKAGES = {python_repr(manifest["packages"])}
MESSAGE_NAMES = {python_repr(manifest["message_names"])}
ENUM_NAMES = {python_repr(manifest["enum_names"])}
TRANSPORT_TOPOLOGY = {python_repr(manifest["transport_topology"])}
"""

    (package_root / "manifest.py").write_text(manifest_text, encoding="utf-8")
    (package_root / "__init__.py").write_text(
        """from .manifest import (
    ENUM_NAMES,
    MESSAGE_NAMES,
    PACKAGES,
    SOURCE_DIGEST,
    SOURCE_FILES,
    TRANSPORT_TOPOLOGY,
)

__all__ = [
    "ENUM_NAMES",
    "MESSAGE_NAMES",
    "PACKAGES",
    "SOURCE_DIGEST",
    "SOURCE_FILES",
    "TRANSPORT_TOPOLOGY",
]
""",
        encoding="utf-8",
    )


def write_rust_manifest(manifest: dict[str, object]) -> None:
    target = ROOT / "rs" / "crates" / "aegis_contracts_rs" / "src" / "generated" / "mod.rs"
    ensure_parent(target)

    source_files = rust_string_array(manifest["source_files"])
    message_names = rust_string_array(manifest["message_names"])
    enum_names = rust_string_array(manifest["enum_names"])
    topology_json = json.dumps(manifest["transport_topology"], indent=2, sort_keys=True)

    body = f"""// Generated from schema/proto and schema/transport-topology.yaml.

pub const SOURCE_DIGEST: &str = "{manifest["source_digest"]}";
pub const SOURCE_FILES: &[&str] = &{source_files};
pub const MESSAGE_NAMES: &[&str] = &{message_names};
pub const ENUM_NAMES: &[&str] = &{enum_names};
pub const TRANSPORT_TOPOLOGY_JSON: &str = r#"{topology_json}"#;
"""
    target.write_text(body, encoding="utf-8")


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def to_elixir(value: object) -> str:
    if value is None:
        return "nil"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return repr(value)
    if isinstance(value, str):
        return json.dumps(value, ensure_ascii=False)
    if isinstance(value, list):
        return "[" + ", ".join(to_elixir(item) for item in value) + "]"
    if isinstance(value, dict):
        items = ", ".join(
            f"{to_elixir(str(key))} => {to_elixir(item)}"
            for key, item in sorted(value.items(), key=lambda pair: str(pair[0]))
        )
        return "%{" + items + "}"
    raise TypeError(f"Unsupported value for Elixir generation: {value!r}")


def python_repr(value: object) -> str:
    return repr(value)


def rust_string_array(values: object) -> str:
    if not isinstance(values, list):
        raise TypeError("Rust array generation expects a list")
    return "[" + ", ".join(json.dumps(value) for value in values) + "]"


if __name__ == "__main__":
    main()
