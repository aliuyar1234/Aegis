#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "schema" / "tool-registry.yaml"
TARGET = ROOT / "apps" / "aegis_policy" / "lib" / "aegis" / "policy" / "generated" / "tool_registry.ex"
DANGEROUS_SOURCE = ROOT / "meta" / "dangerous-action-classes.yaml"
DANGEROUS_TARGET = (
    ROOT
    / "apps"
    / "aegis_policy"
    / "lib"
    / "aegis"
    / "policy"
    / "generated"
    / "dangerous_action_catalog.ex"
)


def source_digest(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.relative_to(ROOT).as_posix().encode("utf-8"))
    digest.update(b"\0")
    digest.update(path.read_bytes())
    digest.update(b"\0")
    return digest.hexdigest()


def to_elixir(value) -> str:
    if isinstance(value, dict):
        items = ", ".join(f"{to_elixir(key)} => {to_elixir(item)}" for key, item in value.items())
        return f"%{{{items}}}"
    if isinstance(value, list):
        return "[" + ", ".join(to_elixir(item) for item in value) + "]"
    if value is None:
        return "nil"
    if value is True:
        return "true"
    if value is False:
        return "false"
    if isinstance(value, (int, float)):
        return str(value)
    return json.dumps(value)


def main() -> int:
    registry = yaml.safe_load(SOURCE.read_text(encoding="utf-8"))
    tools = sorted(registry["tools"], key=lambda descriptor: descriptor["tool_id"])
    digest = source_digest(SOURCE)
    dangerous_catalog = yaml.safe_load(DANGEROUS_SOURCE.read_text(encoding="utf-8"))
    dangerous_actions = sorted(
        dangerous_catalog["dangerous_action_classes"], key=lambda item: item["id"]
    )
    dangerous_digest = source_digest(DANGEROUS_SOURCE)

    module = f"""defmodule Aegis.Policy.Generated.ToolRegistry do
  @moduledoc false

  @source_digest "{digest}"
  @source_files ["{SOURCE.relative_to(ROOT).as_posix()}"]
  @registry_version {registry["registry_version"]}
  @tools {to_elixir(tools)}
  @by_tool_id Map.new(@tools, &{{Map.fetch!(&1, "tool_id"), &1}})

  def source_digest, do: @source_digest
  def source_files, do: @source_files
  def registry_version, do: @registry_version
  def tools, do: @tools
  def by_tool_id, do: @by_tool_id
end
"""

    TARGET.parent.mkdir(parents=True, exist_ok=True)
    TARGET.write_text(module, encoding="utf-8")

    dangerous_module = f"""defmodule Aegis.Policy.Generated.DangerousActionCatalog do
  @moduledoc false

  @source_digest "{dangerous_digest}"
  @source_files ["{DANGEROUS_SOURCE.relative_to(ROOT).as_posix()}"]
  @dangerous_action_classes {to_elixir(dangerous_actions)}
  @by_id Map.new(@dangerous_action_classes, &{{Map.fetch!(&1, "id"), &1}})

  def source_digest, do: @source_digest
  def source_files, do: @source_files
  def dangerous_action_classes, do: @dangerous_action_classes
  def by_id, do: @by_id
end
"""

    DANGEROUS_TARGET.parent.mkdir(parents=True, exist_ok=True)
    DANGEROUS_TARGET.write_text(dangerous_module, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
