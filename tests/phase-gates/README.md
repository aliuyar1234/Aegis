# Phase gates

Phase gates are machine-checkable YAML scenario definitions.
Validate them with:

```bash
python3 scripts/run_phase_gate.py \
  tests/phase-gates/internal-demo.yaml \
  tests/phase-gates/public-demo.yaml \
  tests/phase-gates/enterprise-readiness.yaml \
  tests/phase-gates/oss-managed-split.yaml \
  tests/phase-gates/media-expansion.yaml
```

Each phase gate must validate against `schema/jsonschema/phase-gate.schema.json`.
YAML is authoritative; there are no prose-only phase-gate sources of truth.
