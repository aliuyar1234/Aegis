# Contracts and versioning

Aegis uses explicit, versioned contracts to keep Elixir, Python, and Rust coherent.

## Canonical sources

- Protobuf runtime contracts: `schema/proto/`
- JSON Schemas: `schema/jsonschema/`
- Event registry and payload mapping: `schema/event-catalog/`
- Transport topology: `schema/transport-topology.yaml`
- Codegen config: `buf.yaml`, `buf.gen.yaml`

## Rules

- Runtime control messages use Protobuf.
- Tool I/O, browser fixtures, operator-facing payloads, and security payloads use JSON Schema.
- Every event type has a payload schema and version mapping.
- Workers register supported contract versions.
- Breaking changes require migration notes in `schema/versioning.md`.

## Reproducibility

- `buf.yaml` uses Buf v2 workspace syntax with `schema/proto/` as the canonical module path.
- `buf.gen.yaml` uses Buf v2 `remote:` plugins and pins the Python plugin to `buf.build/protocolbuffers/python:v33.5` so generated Python bindings match the repository's vendored `protobuf 6.33.5` runtime under `py/vendor/`.
- `scripts/generate_contracts.sh` prefers local Buf, falls back to Dockerized Buf (`bufbuild/buf:1.66.0` by default), and persists a Buf cache directory for repeatable local runs.
- `scripts/generate_contract_manifests.py` emits language-consumable manifests with a shared source digest.
- `scripts/validate_schemas.py` rejects stale generated manifests and validates the checked-in Python bindings directly against the canonical `.proto` definitions while forcing imports through the vendored runtime under `py/vendor/`.
- Rust generation remains configured through Buf, but the repository currently treats checked-in Rust protobuf source regeneration as best-effort in environments that hit anonymous BSR plugin rate limits.

## Elixir contract consumption

Elixir must consume the same canonical `.proto` sources as Python and Rust. The control plane is not allowed to fork runtime messages into ad hoc Elixir-only structs. The chosen Elixir protobuf library may change later, but `schema/proto/` remains the SSOT.

At the moment, Elixir still ships a generated manifest module rather than checked-in protobuf bindings. That remains an explicit follow-up item: the repo now proves Buf lint/codegen, manifest freshness, and real Python binding importability, but Elixir still needs a final library choice and build integration step.
