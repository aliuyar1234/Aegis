# Protobuf contracts

`schema/proto/` is the canonical runtime contract surface.

## Generation targets

- Buf codegen is configured in `buf.gen.yaml` for Python and Rust outputs.
- Reproducible contract manifests are generated into:
  - `apps/aegis_execution_bridge/lib/aegis/execution_bridge/generated/`
  - `py/packages/aegis_contracts_py/generated/`
  - `rs/crates/aegis_contracts_rs/src/generated/`
- Real generated Python bindings are written under `py/packages/aegis_contracts_py/generated/proto/`.
- Rust protobuf output is configured for `rs/crates/aegis_contracts_rs/src/generated/proto/` when Buf codegen is available.

## Elixir strategy

Elixir is the control plane and must consume the same canonical `.proto` sources. The repository intentionally keeps `.proto` files as the source of truth and expects the Elixir implementation to compile or generate from them inside the Elixir build using a protobuf library such as Protox or an equivalent generator chosen by the implementation phase.

The important rule is not the specific Elixir library; it is that Elixir must not fork the contract definitions away from `schema/proto/`.

## Generation

Use:

```bash
bash scripts/generate_contracts.sh
```

Generation prefers:

1. local `buf`
2. Dockerized Buf via `bufbuild/buf:1.66.0`
3. manifest refresh only when neither Buf path is available

Useful environment overrides:

- `AEGIS_BUF_MODE=auto|local|docker|manifest-only`
- `AEGIS_BUF_DOCKER_IMAGE=bufbuild/buf:1.66.0`
- `AEGIS_BUF_CACHE_DIR=/path/to/cache`

The Python plugin is pinned to `buf.build/protocolbuffers/python:v33.5` so the checked-in bindings stay compatible with the repository's vendored `protobuf 6.33.5` runtime under `py/vendor/`.

`scripts/generate_contract_manifests.py` remains the reproducible manifest path used by validators. `scripts/validate_schemas.py` now also imports the generated Python bindings directly so contract drift is caught at the binding layer, not only through manifest digests.
