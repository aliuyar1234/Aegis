# Author A Simulation Fixture

## Purpose

This runbook documents the bounded workflow for adding a new deterministic simulation
fixture in PHASE-14.

The fixture authoring flow is intentionally simple:

1. scaffold a valid scenario file
2. customize the scenario steps and expected terminal state
3. validate the scenario locally
4. register it in the manifest only when the fixture is ready

## Scaffold a starting fixture

Create a valid scenario skeleton:

```bash
python scripts/scaffold_simulation_fixture.py tests/simulation/fixtures/my-scenario.yaml --scenario-id my-scenario
```

Optional templates:

- `worker_crash_recovery`
- `approval_timeout`

Example:

```bash
python scripts/scaffold_simulation_fixture.py tests/simulation/fixtures/my-approval-timeout.yaml --scenario-id my-approval-timeout --template approval_timeout
```

## What the scaffold does not do

The scaffold script does not auto-register the new fixture in `meta/simulation-scenarios.yaml`.
That registration step stays manual so contributors cannot smuggle hidden scenario changes
into the manifest without reviewing the SSOT diff.

## Validate the fixture

Run the deterministic scenario runner directly:

```bash
python scripts/run_simulation_scenario.py tests/simulation/fixtures/my-scenario.yaml
```

Then run the broader validation surfaces:

```bash
pytest tests/simulation -q
python scripts/validate_schemas.py
```

## Register the fixture

Only after the scenario is valid and intentional:

- add it to `meta/simulation-scenarios.yaml`
- add replay-diff coverage in `meta/replay-fixtures.yaml` if the scenario must participate in replay differential checks
- add benchmark coverage in `meta/benchmark-corpus.yaml` if the scenario belongs in the correctness scorecard

## Review checklist

- the scenario id is stable and lowercase
- the steps are deterministic and use only supported step kinds
- the expected terminal state is explicit
- the proves list says what the fixture exists to guard
- the scenario does not call real browsers, models, or external services
