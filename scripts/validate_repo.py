#!/usr/bin/env python3
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def phase_num(phase_id: str) -> int:
    return int(phase_id.split('-')[1])


checks = yaml.safe_load((ROOT / 'meta/repo-checks.yaml').read_text(encoding='utf-8'))
required_paths = checks.get('required_paths', [])
forbidden = checks.get('forbidden_phrases', [])
allow_forbidden = set(checks.get('allow_forbidden_in', [])) | {'meta/repo-checks.yaml'}
forbidden_paths = checks.get('forbidden_paths', [])
max_agents_lines = int(checks.get('max_agents_lines', 120))

missing = [p for p in required_paths if not (ROOT / p).exists()]
if missing:
    print('Missing required paths:')
    for p in missing:
        print(' -', p)
    sys.exit(1)

for token in forbidden_paths:
    for path in ROOT.rglob(token):
        print(f'Forbidden cache/noise path present: {path.relative_to(ROOT)}')
        sys.exit(1)

agents_lines = (ROOT / 'AGENTS.md').read_text(encoding='utf-8').splitlines()
if len(agents_lines) > max_agents_lines:
    print(f'AGENTS.md too long: {len(agents_lines)} lines > {max_agents_lines}')
    sys.exit(1)

for path in ROOT.rglob('*'):
    if not path.is_file():
        continue
    rel = path.relative_to(ROOT).as_posix()
    if rel in allow_forbidden:
        continue
    if path.suffix.lower() not in {'.md', '.yaml', '.yml', '.json', '.proto', '.py', '.sh', '.toml', '.ex', '.exs', '.sql'}:
        continue
    text = path.read_text(encoding='utf-8', errors='ignore').lower()
    for phrase in forbidden:
        if phrase.lower() in text:
            print(f'Forbidden phrase found in {rel}: {phrase}')
            sys.exit(1)

phase_data = yaml.safe_load((ROOT / 'meta/phase-gates.yaml').read_text(encoding='utf-8'))['phases']
phase_ids = {p['id']: p for p in phase_data}
current = yaml.safe_load((ROOT / 'meta/current-phase.yaml').read_text(encoding='utf-8'))
current_id = current['current_phase']
current_doc = current['current_phase_doc']

if current_id not in phase_ids:
    print(f'Current phase {current_id} missing from meta/phase-gates.yaml')
    sys.exit(1)
if phase_ids[current_id]['status'] != 'current':
    print(f'Current phase {current_id} must have status=current')
    sys.exit(1)
if phase_ids[current_id]['doc'] != current_doc:
    print(f'current_phase_doc mismatch: {current_doc} != {phase_ids[current_id]["doc"]}')
    sys.exit(1)
if not (ROOT / current_doc).exists():
    print(f'current_phase_doc missing: {current_doc}')
    sys.exit(1)
if sum(1 for p in phase_data if p['status'] == 'current') != 1:
    print('Exactly one phase must have status=current')
    sys.exit(1)
for completed in current.get('completed_phases', []):
    if phase_ids[completed]['status'] != 'completed':
        print(f'Completed phase {completed} must have status=completed')
        sys.exit(1)

tasks = {t['id']: t for t in yaml.safe_load((ROOT / 'work-items/task-index.yaml').read_text(encoding='utf-8'))['tasks']}
for task_id in current.get('starting_sequence', []):
    if task_id not in tasks:
        print(f'Starting sequence task missing: {task_id}')
        sys.exit(1)
    if phase_num(tasks[task_id]['phase']) < phase_num(current_id):
        print(f'Starting sequence task {task_id} points backward to an earlier phase')
        sys.exit(1)

link_re = re.compile(r'\[[^\]]+\]\(([^)]+)\)')
workflow_uses_re = re.compile(r'^\s*-\s*uses:\s*([^\s#]+)', re.MULTILINE)
sha_ref_re = re.compile(r'^[0-9a-f]{40}$')
for md in ROOT.rglob('*.md'):
    rel_md = md.relative_to(ROOT).as_posix()
    text = md.read_text(encoding='utf-8', errors='ignore')
    for target in link_re.findall(text):
        if target.startswith(('http://', 'https://', 'mailto:', '#')):
            continue
        target_path = target.split('#', 1)[0]
        if not target_path:
            continue
        resolved = (md.parent / target_path).resolve()
        try:
            resolved.relative_to(ROOT.resolve())
        except Exception:
            print(f'Link escapes repo in {rel_md}: {target}')
            sys.exit(1)
        if not resolved.exists():
            print(f'Broken markdown link in {rel_md}: {target}')
            sys.exit(1)

for workflow in (ROOT / '.github' / 'workflows').glob('*.yml'):
    rel_workflow = workflow.relative_to(ROOT).as_posix()
    text = workflow.read_text(encoding='utf-8', errors='ignore')
    for action_ref in workflow_uses_re.findall(text):
        if action_ref.startswith('./') or action_ref.startswith('docker://'):
            continue
        if '@' not in action_ref:
            print(f'Workflow action ref missing version in {rel_workflow}: {action_ref}')
            sys.exit(1)
        ref = action_ref.rsplit('@', 1)[1]
        if sha_ref_re.fullmatch(ref) is None:
            print(f'Workflow action is not SHA-pinned in {rel_workflow}: {action_ref}')
            sys.exit(1)

for suite in yaml.safe_load((ROOT / 'meta/test-suites.yaml').read_text(encoding='utf-8'))['test_suites']:
    for rel in suite.get('paths', []):
        if not (ROOT / rel).exists():
            print(f"Test suite {suite['id']} path missing: {rel}")
            sys.exit(1)

subprocess.run([sys.executable, str(ROOT / 'scripts/generate_docs.py'), '--check'], check=True)
print('Repo validation passed.')
