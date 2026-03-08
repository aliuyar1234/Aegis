#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import io
import sys
from pathlib import Path
from typing import Dict, List

import yaml

ROOT = Path(__file__).resolve().parents[1]


def load_yaml(rel: str):
    return yaml.safe_load((ROOT / rel).read_text(encoding="utf-8"))


def phase_sort_key(phase_id: str) -> int:
    try:
        return int(phase_id.split("-")[1])
    except Exception:
        return 999


def render_tasks_csv(tasks: List[dict]) -> str:
    buf = io.StringIO()
    writer = csv.writer(buf, lineterminator='\n')
    writer.writerow(["task_id", "phase", "title", "critical_path", "deps", "adr_refs", "acceptance_refs", "test_refs", "status"])
    for t in tasks:
        writer.writerow([
            t["id"],
            t["phase"],
            t["title"],
            str(t.get("critical_path", False)),
            ";".join(t.get("deps", [])),
            ";".join(t.get("adr_refs", [])),
            ";".join(t.get("acceptance_refs", [])),
            ";".join(t.get("test_refs", [])),
            t.get("status", "planned"),
        ])
    return buf.getvalue()


def build_traceability(invariants: List[dict], tasks: List[dict], failure_runbooks: List[dict]) -> str:
    by_adr: Dict[str, List[dict]] = {}
    for task in tasks:
        for adr in task.get("adr_refs", []):
            by_adr.setdefault(adr, []).append(task)
    runbook_map = {
        "INV-002": ["docs/runbooks/node-loss.md", "docs/runbooks/lease-ambiguity.md"],
        "INV-004": ["docs/runbooks/transport-lag.md"],
        "INV-008": ["docs/runbooks/operator-intervention.md", "docs/runbooks/approval-timeout.md"],
        "INV-010": ["docs/runbooks/duplicate-execution.md"],
        "INV-013": ["docs/runbooks/lease-ambiguity.md", "docs/runbooks/degraded-system-mode.md"],
        "INV-014": ["docs/runbooks/artifact-store-outage.md"],
        "INV-017": ["docs/runbooks/event-corruption-quarantine.md", "docs/runbooks/operator-intervention.md"],
        "INV-019": ["docs/runbooks/browser-instability.md", "docs/runbooks/approval-timeout.md"],
    }
    buf = io.StringIO()
    writer = csv.writer(buf, lineterminator='\n')
    writer.writerow(["invariant_id", "invariant_title", "adr_id", "phase_ids", "task_ids", "test_ids", "acceptance_ids", "runbooks"])
    for inv in invariants:
        linked_tasks = by_adr.get(inv["adr"], [])
        phase_ids = sorted({t["phase"] for t in linked_tasks}, key=phase_sort_key)
        task_ids = [t["id"] for t in linked_tasks]
        runbooks = runbook_map.get(inv["id"], [])
        writer.writerow([
            inv["id"],
            inv["title"],
            inv["adr"],
            ";".join(phase_ids),
            ";".join(task_ids),
            ";".join(inv.get("tests", [])),
            ";".join(inv.get("acceptance", [])),
            ";".join(runbooks),
        ])
    return buf.getvalue()


def render_phase_task_file(phase: dict, tasks: List[dict]) -> str:
    payload = {
        "phase": phase["id"],
        "status": phase["status"],
        "name": phase["name"],
        "phase_doc": phase["doc"],
        "tasks": tasks,
    }
    return yaml.safe_dump(payload, sort_keys=False, allow_unicode=True)


def ensure_file(rel: str, content: str, check: bool) -> int:
    path = ROOT / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    existing = path.read_text(encoding="utf-8") if path.exists() else None
    if check:
        if existing != content:
            print(f"Stale generated file: {rel}")
            return 1
        return 0
    path.write_text(content, encoding="utf-8")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="Fail if generated artifacts are stale")
    args = parser.parse_args()

    tasks = load_yaml("work-items/task-index.yaml")["tasks"]
    phases = load_yaml("meta/phase-gates.yaml")["phases"]
    invariants = load_yaml("meta/invariants.yaml")["invariants"]
    failure_runbooks = load_yaml("meta/failure-runbooks.yaml")["failures"]

    rc = 0
    tasks_csv = render_tasks_csv(tasks)
    rc |= ensure_file("docs/generated/tasks.csv", tasks_csv, args.check)
    trace_csv = build_traceability(invariants, tasks, failure_runbooks)
    rc |= ensure_file("docs/generated/traceability-matrix.csv", trace_csv, args.check)

    by_phase: Dict[str, List[dict]] = {}
    for task in tasks:
        by_phase.setdefault(task["phase"], []).append(task)
    for phase in phases:
        rel = phase["task_file"]
        content = render_phase_task_file(phase, by_phase.get(phase["id"], []))
        rc |= ensure_file(rel, content, args.check)

    if rc == 0 and not args.check:
        print("Generated docs refreshed.")
    elif rc == 0 and args.check:
        print("Generated docs are fresh.")
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
