#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

import yaml
from jsonschema import validate

ROOT = Path(__file__).resolve().parents[1]
acceptance_meta = {a['id']: a for a in yaml.safe_load((ROOT / 'meta/acceptance-criteria.yaml').read_text(encoding='utf-8'))['acceptance_criteria']}
tests_meta = {t['id']: t for t in yaml.safe_load((ROOT / 'meta/test-suites.yaml').read_text(encoding='utf-8'))['test_suites']}
phases_meta = {p['id']: p for p in yaml.safe_load((ROOT / 'meta/phase-gates.yaml').read_text(encoding='utf-8'))['phases']}
gate_schema = json.loads((ROOT / 'schema/jsonschema/phase-gate.schema.json').read_text(encoding='utf-8'))

def phase_num(phase_id: str) -> int:
    return int(phase_id.split('-')[1])

for gate_path in sys.argv[1:]:
    path = ROOT / gate_path
    if not path.exists():
        print(f'Missing phase gate: {gate_path}')
        sys.exit(1)

    data = yaml.safe_load(path.read_text(encoding='utf-8'))
    validate(data, gate_schema)

    gate_phase = data['phase']
    if gate_phase not in phases_meta:
        print(f'{gate_path} references unknown phase {gate_phase}')
        sys.exit(1)

    for fixture in data['fixtures']:
        fpath = ROOT / fixture
        if not fpath.exists():
            print(f'{gate_path} references missing fixture {fixture}')
            sys.exit(1)

    for ac in data['acceptance']:
        if ac not in acceptance_meta:
            print(f'{gate_path} references unknown acceptance criterion {ac}')
            sys.exit(1)
        if phase_num(acceptance_meta[ac]['phase']) > phase_num(gate_phase):
            print(f'{gate_path} references future-phase acceptance criterion {ac}')
            sys.exit(1)

    for ts in data['tests']:
        if ts not in tests_meta:
            print(f'{gate_path} references unknown test suite {ts}')
            sys.exit(1)
        for test_path in tests_meta[ts].get('paths', []):
            if not (ROOT / test_path).exists():
                print(f'{gate_path} references test suite {ts} with missing path {test_path}')
                sys.exit(1)

    for step in data['steps']:
        if not step['evidence']:
            print(f'{gate_path} step {step["id"]} must include evidence')
            sys.exit(1)

print('Phase gates validated.')
