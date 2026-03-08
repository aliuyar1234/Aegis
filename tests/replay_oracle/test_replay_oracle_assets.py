from pathlib import Path
import json

import yaml
from jsonschema import validate

ROOT = Path(__file__).resolve().parents[2]


def load_yaml(path: str):
    return yaml.safe_load((ROOT / path).read_text(encoding="utf-8"))


def load_schema(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_replay_oracle_docs_and_assets_exist():
    required_paths = [
        "docs/exec-plans/active/PHASE-14-runtime-conformance-simulation.md",
        "docs/design-docs/replay-oracle.md",
        "docs/design-docs/event-replay-model.md",
        "meta/determinism-classes.yaml",
        "meta/replay-equivalence.yaml",
        "schema/jsonschema/determinism-classification.schema.json",
        "schema/jsonschema/replay-oracle.schema.json",
        "tests/phase-gates/phase-14-replay-equivalence.yaml",
    ]

    for path in required_paths:
        assert (ROOT / path).exists(), path


def test_replay_oracle_artifacts_validate_against_schemas():
    schema_pairs = [
        (
            "meta/determinism-classes.yaml",
            "schema/jsonschema/determinism-classification.schema.json",
        ),
        (
            "meta/replay-equivalence.yaml",
            "schema/jsonschema/replay-oracle.schema.json",
        ),
    ]

    for payload_path, schema_path in schema_pairs:
        validate(load_yaml(payload_path), load_schema(schema_path))


def test_phase14_suite_registry_matches_replay_oracle_pytest_contract():
    suites = load_yaml("meta/test-suites.yaml")["test_suites"]
    suite = next(item for item in suites if item["id"] == "TS-019")

    assert suite["command"] == "pytest tests/replay_oracle -q"
    assert "tests/replay_oracle" in suite["paths"]
    assert "meta/determinism-classes.yaml" in suite["paths"]
    assert "meta/replay-equivalence.yaml" in suite["paths"]
    assert "docs/design-docs/replay-oracle.md" in suite["paths"]
    assert "tests/phase-gates/phase-14-replay-equivalence.yaml" in suite["paths"]


def test_phase14_gate_references_replay_oracle_artifacts():
    gate = load_yaml("tests/phase-gates/phase-14-replay-equivalence.yaml")
    fixtures = set(gate["fixtures"])
    step_ids = {step["id"] for step in gate["steps"]}

    assert gate["phase"] == "PHASE-14"
    assert set(gate["tests"]) == {"TS-004", "TS-019"}
    assert set(gate["acceptance"]) == {"AC-057", "AC-058", "AC-059"}
    assert "meta/determinism-classes.yaml" in fixtures
    assert "meta/replay-equivalence.yaml" in fixtures
    assert "schema/jsonschema/determinism-classification.schema.json" in fixtures
    assert "schema/jsonschema/replay-oracle.schema.json" in fixtures
    assert {"determinism-catalog", "replay-modes", "gate-assets"} <= step_ids


def test_replay_oracle_docs_make_boundaries_explicit():
    oracle_doc = (ROOT / "docs/design-docs/replay-oracle.md").read_text(encoding="utf-8").lower()
    replay_doc = (ROOT / "docs/design-docs/event-replay-model.md").read_text(encoding="utf-8").lower()

    assert "captured-nondeterministic" in oracle_doc
    assert "externally-unknowable" in oracle_doc
    assert "historical replay must never call model providers" in oracle_doc
    assert "checkpoint-tail replay must converge with full replay" in oracle_doc
    assert "nondeterministic outputs must be captured as event payloads or artifacts" in replay_doc


def test_replay_oracle_catalogs_cover_modes_classes_and_equivalence_surface():
    classes = load_yaml("meta/determinism-classes.yaml")
    oracle = load_yaml("meta/replay-equivalence.yaml")

    assert [item["id"] for item in classes["classes"]] == [
        "deterministic",
        "captured-nondeterministic",
        "externally-unknowable",
    ]
    assert {item["id"] for item in oracle["modes"]} == {
        "full-replay",
        "checkpoint-tail-replay",
        "historical-replay",
    }
    assert {item["id"] for item in oracle["equivalence_dimensions"]} == {
        "session-state",
        "action-ledger",
        "approval-ledger",
        "artifact-catalog",
        "uncertainty-surface",
    }
    requirement_ids = {item["id"] for item in oracle["requirements"]}
    assert {
        "no-side-effect-reexecution",
        "checkpoint-tail-converges-with-full",
        "unknowable-state-stays-unknowable",
    } <= requirement_ids
