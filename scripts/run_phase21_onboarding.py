#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

import yaml
from jsonschema import validate


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_SCHEMA = json.loads(
    (ROOT / "schema/jsonschema/fresh-clone-onboarding.schema.json").read_text(encoding="utf-8")
)
REPORT_SCHEMA = json.loads(
    (ROOT / "schema/jsonschema/fresh-clone-onboarding-report.schema.json").read_text(
        encoding="utf-8"
    )
)


def load_yaml(rel: str) -> object:
    return yaml.safe_load((ROOT / rel).read_text(encoding="utf-8"))


def main() -> int:
    manifest = load_yaml("meta/fresh-clone-onboarding.yaml")
    validate(instance=manifest, schema=MANIFEST_SCHEMA)

    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    makefile = (ROOT / "Makefile").read_text(encoding="utf-8")

    checks: list[dict[str, str]] = []

    checks.append(
        {
            "name": "canonical-docs-exist",
            "verdict": "pass"
            if all((ROOT / rel).exists() for rel in manifest["canonical_docs"])
            else "fail",
        }
    )
    checks.append(
        {
            "name": "read-order-paths-exist",
            "verdict": "pass"
            if all((ROOT / rel).exists() for rel in manifest["read_order"])
            else "fail",
        }
    )
    checks.append(
        {
            "name": "agents-read-order-aligned",
            "verdict": "pass"
            if all(ref in agents for ref in manifest["agents_required_refs"])
            else "fail",
        }
    )
    checks.append(
        {
            "name": "readme-first-run-aligned",
            "verdict": "pass"
            if all(snippet in readme for snippet in manifest["readme_required_snippets"])
            else "fail",
        }
    )
    checks.append(
        {
            "name": "make-targets-exist",
            "verdict": "pass"
            if all(
                target in makefile
                for target in ["bootstrap:", "eval-up:", "eval-init:", "eval-check:", "eval-ready:", "smoke:"]
            )
            else "fail",
        }
    )
    checks.append(
        {
            "name": "required-scripts-exist",
            "verdict": "pass"
            if all((ROOT / rel).exists() for rel in manifest["required_scripts"])
            else "fail",
        }
    )

    report = {
        "id": "phase21-fresh-clone-onboarding-report",
        "checks": checks,
        "verdict": "pass" if all(item["verdict"] == "pass" for item in checks) else "fail",
    }
    validate(instance=report, schema=REPORT_SCHEMA)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["verdict"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
