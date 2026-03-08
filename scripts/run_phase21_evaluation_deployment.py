#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

import yaml
from jsonschema import validate


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_SCHEMA = json.loads(
    (ROOT / "schema/jsonschema/evaluation-deployment-profile.schema.json").read_text(
        encoding="utf-8"
    )
)
REPORT_SCHEMA = json.loads(
    (ROOT / "schema/jsonschema/evaluation-deployment-report.schema.json").read_text(
        encoding="utf-8"
    )
)


def load_yaml(rel: str) -> object:
    return yaml.safe_load((ROOT / rel).read_text(encoding="utf-8"))


def exposed_ports(service_payload: dict[str, object]) -> set[int]:
    ports: set[int] = set()
    for raw in service_payload.get("ports", []):
        token = str(raw).split(":")[0]
        if token.isdigit():
            ports.add(int(token))
    return ports


def main() -> int:
    manifest = load_yaml("meta/evaluation-deployment-profile.yaml")
    validate(instance=manifest, schema=MANIFEST_SCHEMA)

    compose = load_yaml(manifest["compose_file"])
    makefile = (ROOT / "Makefile").read_text(encoding="utf-8")
    services = compose["services"]

    service_results = []
    for service in manifest["services"]:
        payload = services.get(service["name"])
        verdict = "pass"
        port_count = 0
        if payload is None:
            verdict = "fail"
        else:
            ports = exposed_ports(payload)
            port_count = len(ports)
            if not set(service["required_ports"]).issubset(ports):
                verdict = "fail"
        service_results.append(
            {
                "name": service["name"],
                "port_count": port_count,
                "verdict": verdict,
            }
        )

    target_results = []
    for target in manifest["required_targets"]:
        verdict = "pass" if f"{target}:" in makefile else "fail"
        target_results.append({"name": target, "verdict": verdict})

    target_results.append(
        {
            "name": "required-docs",
            "verdict": "pass"
            if all((ROOT / rel).exists() for rel in manifest["required_docs"])
            else "fail",
        }
    )
    target_results.append(
        {
            "name": "required-scripts",
            "verdict": "pass"
            if all((ROOT / rel).exists() for rel in manifest["init_scripts"] + manifest["smoke_scripts"])
            else "fail",
        }
    )

    report = {
        "id": "phase21-evaluation-deployment-report",
        "services": service_results,
        "targets": target_results,
        "verdict": "pass"
        if all(item["verdict"] == "pass" for item in service_results + target_results)
        else "fail",
    }
    validate(instance=report, schema=REPORT_SCHEMA)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["verdict"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
