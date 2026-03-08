#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]

def phase_num(phase_id: str) -> int:
    return int(phase_id.split('-')[1])

invariants = {i['id']: i for i in yaml.safe_load((ROOT / 'meta/invariants.yaml').read_text(encoding='utf-8'))['invariants']}
adrs = {a['id']: a for a in yaml.safe_load((ROOT / 'meta/adr-index.yaml').read_text(encoding='utf-8'))['adrs']}
acceptance = {a['id']: a for a in yaml.safe_load((ROOT / 'meta/acceptance-criteria.yaml').read_text(encoding='utf-8'))['acceptance_criteria']}
tests = {t['id']: t for t in yaml.safe_load((ROOT / 'meta/test-suites.yaml').read_text(encoding='utf-8'))['test_suites']}
phases = {p['id']: p for p in yaml.safe_load((ROOT / 'meta/phase-gates.yaml').read_text(encoding='utf-8'))['phases']}
tasks = {t['id']: t for t in yaml.safe_load((ROOT / 'work-items/task-index.yaml').read_text(encoding='utf-8'))['tasks']}
current = yaml.safe_load((ROOT / 'meta/current-phase.yaml').read_text(encoding='utf-8'))

for inv in invariants.values():
    if inv['adr'] not in adrs:
        print(f"Invariant {inv['id']} points to missing ADR {inv['adr']}")
        sys.exit(1)
    for ac in inv.get('acceptance', []):
        if ac not in acceptance:
            print(f"Invariant {inv['id']} points to missing acceptance {ac}")
            sys.exit(1)
    for ts in inv.get('tests', []):
        if ts not in tests:
            print(f"Invariant {inv['id']} points to missing test suite {ts}")
            sys.exit(1)

for task in tasks.values():
    if task['phase'] not in phases:
        print(f"Task {task['id']} points to unknown phase {task['phase']}")
        sys.exit(1)
    for dep in task.get('deps', []):
        if dep not in tasks:
            print(f"Task {task['id']} depends on missing task {dep}")
            sys.exit(1)
        if phase_num(tasks[dep]['phase']) > phase_num(task['phase']):
            print(f"Task {task['id']} depends on later-phase task {dep}")
            sys.exit(1)
    for adr in task.get('adr_refs', []):
        if adr not in adrs:
            print(f"Task {task['id']} points to missing ADR {adr}")
            sys.exit(1)
    for ac in task.get('acceptance_refs', []):
        if ac not in acceptance:
            print(f"Task {task['id']} points to missing acceptance {ac}")
            sys.exit(1)
        if phase_num(acceptance[ac]['phase']) > phase_num(task['phase']):
            print(f"Task {task['id']} references future-phase acceptance {ac}")
            sys.exit(1)
    for ts in task.get('test_refs', []):
        if ts not in tests:
            print(f"Task {task['id']} points to missing test suite {ts}")
            sys.exit(1)

# Phase order sanity
for phase in phases.values():
    for prereq in phase.get('prereqs', []):
        if prereq not in phases:
            print(f"Phase {phase['id']} has missing prereq {prereq}")
            sys.exit(1)
        if phase_num(prereq) >= phase_num(phase['id']):
            print(f"Phase {phase['id']} has invalid prereq order {prereq}")
            sys.exit(1)
    for unlocked in phase.get('unlocks', []):
        if unlocked not in phases:
            print(f"Phase {phase['id']} unlocks missing phase {unlocked}")
            sys.exit(1)
        if phase_num(unlocked) <= phase_num(phase['id']):
            print(f"Phase {phase['id']} has backward unlock {unlocked}")
            sys.exit(1)

# PHASE-00 must be complete if current phase is later
if phase_num(current['current_phase']) > 0:
    for task in tasks.values():
        if task['phase'] == 'PHASE-00' and task['status'] != 'done':
            print('PHASE-00 task is not done even though current phase is later')
            sys.exit(1)


# Current-phase starting sequence sanity
for task_id in current.get('starting_sequence', []):
    if task_id not in tasks:
        print(f"Current phase starting task missing: {task_id}")
        sys.exit(1)
    if tasks[task_id]['status'] == 'done':
        print(f"Current phase starting task already marked done: {task_id}")
        sys.exit(1)

print('Traceability validation passed.')
