#!/usr/bin/env python3
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]
phases = yaml.safe_load((ROOT / 'meta/phase-gates.yaml').read_text(encoding='utf-8'))['phases']
phase_order = {p['id']: idx for idx, p in enumerate(phases)}
current = yaml.safe_load((ROOT / 'meta/current-phase.yaml').read_text(encoding='utf-8'))
current_phase = current['current_phase']
tasks = yaml.safe_load((ROOT / 'work-items/task-index.yaml').read_text(encoding='utf-8'))['tasks']
by_id = {t['id']: t for t in tasks}
completed = {t['id'] for t in tasks if t['status'] == 'done'}
phase_complete = {
    phase['id']: all(t['status'] == 'done' for t in tasks if t['phase'] == phase['id'])
    for phase in phases
}


def unblocked_for_phase(phase_id: str):
    result = []
    for t in tasks:
        if t['phase'] != phase_id or t['status'] != 'planned':
            continue
        if all(dep in completed for dep in t.get('deps', [])):
            result.append(t)
    return sorted(result, key=lambda t: (not t.get('critical_path', False), t['id']))

current_unblocked = unblocked_for_phase(current_phase)
print(f"Current phase: {current_phase}")
if current_unblocked:
    print('Unblocked tasks in current phase:')
    for t in current_unblocked[:10]:
        deps = ', '.join(t.get('deps', [])) if t.get('deps') else 'none'
        print(f"- {t['id']} {t['title']} | critical={t.get('critical_path', False)} | deps={deps}")
else:
    print('No unblocked tasks in current phase. Looking for next unlocked phase...')
    completed_phases = set(current.get('completed_phases', []))
    for phase in phases:
        pid = phase['id']
        if phase_order[pid] <= phase_order[current_phase]:
            continue
        if all(req in completed_phases or req == current_phase or phase_complete.get(req, False) for req in phase.get('prereqs', [])):
            next_tasks = unblocked_for_phase(pid)
            if not next_tasks:
                continue
            print(f"Next candidate phase: {pid}")
            for t in next_tasks[:10]:
                deps = ', '.join(t.get('deps', [])) if t.get('deps') else 'none'
                print(f"- {t['id']} {t['title']} | critical={t.get('critical_path', False)} | deps={deps}")
            break
