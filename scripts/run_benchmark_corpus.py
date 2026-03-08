#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

import yaml
from jsonschema import validate

ROOT = Path(__file__).resolve().parents[1]
CORPUS_SCHEMA = json.loads(
    (ROOT / "schema/jsonschema/benchmark-corpus.schema.json").read_text(encoding="utf-8")
)
BUDGET_SCHEMA = json.loads(
    (ROOT / "schema/jsonschema/performance-budgets.schema.json").read_text(encoding="utf-8")
)
RUN_SCHEMA = json.loads(
    (ROOT / "schema/jsonschema/benchmark-run.schema.json").read_text(encoding="utf-8")
)
SCORECARD_SCHEMA = json.loads(
    (ROOT / "schema/jsonschema/benchmark-scorecard.schema.json").read_text(encoding="utf-8")
)

MODE_OVERHEAD_MS = {
    "full_replay": 25,
    "checkpoint_tail_vs_full": 60,
    "historical_replay": 40,
}


def load_yaml(path: Path) -> object:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def run_scenario(path: str) -> dict:
    completed = subprocess.run(
        [sys.executable, "scripts/run_simulation_scenario.py", path],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(completed.stdout)


def run_replay_diff() -> dict:
    completed = subprocess.run(
        [sys.executable, "scripts/run_replay_diff.py", "meta/replay-fixtures.yaml"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(completed.stdout)


def merged_budgets(budget_manifest: dict, case_id: str, profile_id: str) -> dict:
    profiles = {item["id"]: item["budgets"] for item in budget_manifest["profiles"]}
    profile = dict(profiles[profile_id])
    for override in budget_manifest.get("case_overrides", []):
        if override["benchmark_case"] == case_id:
            profile.update(override["budgets"])
    return profile


def estimated_runtime_ms(scenario_result: dict, comparison_mode: str) -> int:
    event_count = len(scenario_result["emitted_events"])
    fault_count = len(scenario_result["faults_applied"])
    artifact_count = sum(
        1 for event in scenario_result["emitted_events"] if event["event_type"] == "artifact.registered"
    )
    return (
        40
        + (event_count * 30)
        + (fault_count * 90)
        + (artifact_count * 15)
        + MODE_OVERHEAD_MS[comparison_mode]
    )


def correctness_score(replay_fixture: dict) -> int:
    score = 100
    if not replay_fixture["current_signature_match"]:
        score -= 50
    if not replay_fixture["previous_supported_equivalent"]:
        score -= 50
    return max(score, 0)


def build_run(case: dict, budget_manifest: dict, replay_result: dict) -> dict:
    scenario_result = run_scenario(case["scenario_ref"])
    budgets = merged_budgets(budget_manifest, case["id"], case["budget_profile"])
    metrics = {
        "event_count": len(scenario_result["emitted_events"]),
        "fault_count": len(scenario_result["faults_applied"]),
        "artifact_count": sum(
            1 for event in scenario_result["emitted_events"] if event["event_type"] == "artifact.registered"
        ),
        "estimated_runtime_ms": estimated_runtime_ms(scenario_result, replay_result["comparison_mode"]),
        "correctness_score": correctness_score(replay_result),
        "current_signature_match": replay_result["current_signature_match"],
        "previous_supported_equivalent": replay_result["previous_supported_equivalent"],
    }
    budget_evaluation = {
        "event_count_within_budget": metrics["event_count"] <= budgets["max_event_count"],
        "fault_count_within_budget": metrics["fault_count"] <= budgets["max_fault_count"],
        "artifact_count_within_budget": metrics["artifact_count"] <= budgets["max_artifact_count"],
        "estimated_runtime_within_budget": metrics["estimated_runtime_ms"] <= budgets["max_estimated_runtime_ms"],
        "correctness_score_within_budget": metrics["correctness_score"] >= budgets["min_correctness_score"],
    }
    run = {
        "id": f"benchmark-run-{case['id']}",
        "benchmark_case": case["id"],
        "scenario_id": scenario_result["scenario_id"],
        "replay_fixture_id": case["replay_fixture_id"],
        "budget_profile": case["budget_profile"],
        "metrics": metrics,
        "budget_evaluation": budget_evaluation,
        "verdict": (
            "pass"
            if replay_result["verdict"] == "pass" and all(budget_evaluation.values())
            else "fail"
        ),
    }
    validate(instance=run, schema=RUN_SCHEMA)
    return run


def build_scorecard(corpus: dict, budget_manifest: dict, replay_report: dict) -> dict:
    replay_map = {item["fixture_id"]: item for item in replay_report["fixture_results"]}
    runs = [build_run(case, budget_manifest, replay_map[case["replay_fixture_id"]]) for case in corpus["cases"]]
    scorecard = {
        "id": "phase-14-benchmark-scorecard",
        "corpus_id": corpus["id"],
        "budget_manifest_id": budget_manifest["id"],
        "cost_model_id": corpus["cost_model"]["id"],
        "cases": runs,
        "summary": {
            "case_count": len(runs),
            "passed": sum(1 for item in runs if item["verdict"] == "pass"),
            "failed": sum(1 for item in runs if item["verdict"] == "fail"),
        },
        "overall_verdict": "pass" if all(item["verdict"] == "pass" for item in runs) else "fail",
    }
    validate(instance=scorecard, schema=SCORECARD_SCHEMA)
    return scorecard


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("corpus", help="Path to benchmark corpus YAML")
    parser.add_argument("budgets", help="Path to performance budgets YAML")
    parser.add_argument("--write", help="Optional output path for the generated scorecard")
    args = parser.parse_args(argv[1:])

    corpus_path = ROOT / args.corpus
    budget_path = ROOT / args.budgets
    corpus = load_yaml(corpus_path)
    budget_manifest = load_yaml(budget_path)
    validate(instance=corpus, schema=CORPUS_SCHEMA)
    validate(instance=budget_manifest, schema=BUDGET_SCHEMA)

    replay_report = run_replay_diff()
    scorecard = build_scorecard(corpus, budget_manifest, replay_report)

    rendered = json.dumps(scorecard, indent=2, sort_keys=True)
    if args.write:
        output_path = ROOT / args.write
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(f"{rendered}\n", encoding="utf-8")

    print(rendered)
    return 0 if scorecard["overall_verdict"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
