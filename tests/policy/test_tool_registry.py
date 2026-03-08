import json
from pathlib import Path

import yaml
from jsonschema import validate

ROOT = Path(__file__).resolve().parents[2]


def load_json(relative_path: str):
    return json.loads((ROOT / relative_path).read_text(encoding="utf-8"))


def test_tool_registry_catalog_validates_against_tool_descriptor_schema():
    registry = yaml.safe_load((ROOT / "schema/tool-registry.yaml").read_text(encoding="utf-8"))
    descriptor_schema = load_json("schema/jsonschema/tool-descriptor.schema.json")
    dangerous_classes = yaml.safe_load((ROOT / "meta/dangerous-action-classes.yaml").read_text(encoding="utf-8"))
    dangerous_ids = {item["id"] for item in dangerous_classes["dangerous_action_classes"]}

    assert registry["registry_version"] == 1

    seen = set()
    for descriptor in registry["tools"]:
        validate(instance=descriptor, schema=descriptor_schema)
        assert descriptor["tool_id"] not in seen
        seen.add(descriptor["tool_id"])

        assert (ROOT / descriptor["input_schema_ref"]).exists()
        assert (ROOT / descriptor["output_schema_ref"]).exists()

        dangerous_action_class = descriptor["dangerous_action_class"]
        if dangerous_action_class is not None:
            assert dangerous_action_class in dangerous_ids


def test_tool_registry_contains_current_browser_tools():
    registry = yaml.safe_load((ROOT / "schema/tool-registry.yaml").read_text(encoding="utf-8"))
    descriptors = {item["tool_id"]: item for item in registry["tools"]}

    assert set(descriptors) == {
        "browser.click",
        "browser.delete",
        "browser.navigate",
        "browser.open",
        "browser.submit",
    }
    assert descriptors["browser.navigate"]["required_scopes"] == ["browser.navigate", "artifact.capture"]
    assert descriptors["browser.open"]["required_scopes"] == ["browser.context.open"]
    assert descriptors["browser.click"]["dangerous_action_class"] == "browser_write_low"
    assert descriptors["browser.submit"]["dangerous_action_class"] == "browser_write_medium"
    assert descriptors["browser.delete"]["dangerous_action_class"] == "browser_write_high"
