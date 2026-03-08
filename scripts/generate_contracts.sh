#!/usr/bin/env bash
set -euo pipefail

BUF_MODE="${AEGIS_BUF_MODE:-auto}"
BUF_DOCKER_IMAGE="${AEGIS_BUF_DOCKER_IMAGE:-bufbuild/buf:1.66.0}"
BUF_CACHE_DIR="${AEGIS_BUF_CACHE_DIR:-${HOME}/.cache/aegis-buf}"

buf_runner() {
  case "${BUF_MODE}" in
    auto|local)
      if command -v buf >/dev/null 2>&1; then
        buf "$@"
        return 0
      fi
      if [[ "${BUF_MODE}" == "local" ]]; then
        echo "AEGIS_BUF_MODE=local but buf is not installed." >&2
        return 127
      fi
      ;&
    auto|docker)
      if command -v docker >/dev/null 2>&1; then
        local workspace
        local cache_dir
        workspace="$(pwd)"
        cache_dir="${BUF_CACHE_DIR}"
        if command -v cygpath >/dev/null 2>&1; then
          workspace="$(cygpath -am "${workspace}")"
          cache_dir="$(cygpath -am "${cache_dir}")"
        fi
        mkdir -p "${cache_dir}"
        docker run --rm \
          -e BUF_CACHE_DIR=/root/.cache/buf \
          -v "${cache_dir}:/root/.cache/buf" \
          -v "${workspace}:/workspace" \
          -w /workspace \
          "${BUF_DOCKER_IMAGE}" \
          "$@"
        return 0
      fi
      if [[ "${BUF_MODE}" == "docker" ]]; then
        echo "AEGIS_BUF_MODE=docker but docker is not available." >&2
        return 127
      fi
      ;;
    manifest-only)
      return 127
      ;;
    *)
      echo "Unsupported AEGIS_BUF_MODE: ${BUF_MODE}" >&2
      return 2
      ;;
  esac

  return 127
}

write_binding_markers() {
  local digest
  digest="$(
    python3 - <<'PY'
import importlib.util
from pathlib import Path

manifest_path = Path("py/packages/aegis_contracts_py/generated/manifest.py")
spec = importlib.util.spec_from_file_location("aegis_contract_manifest", manifest_path)
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(module)
print(module.SOURCE_DIGEST)
PY
  )"

  mkdir -p py/packages/aegis_contracts_py/generated/proto
  printf '%s\n' "${digest}" > py/packages/aegis_contracts_py/generated/proto/.source_digest

  mkdir -p rs/crates/aegis_contracts_rs/src/generated/proto
  printf '%s\n' "${digest}" > rs/crates/aegis_contracts_rs/src/generated/proto/.source_digest
}

generated_real_bindings=0

if buf_runner --version >/dev/null 2>&1; then
  buf_runner lint
  buf_runner generate
  generated_real_bindings=1
else
  echo "Buf unavailable; generated manifest refresh only." >&2
fi

python3 scripts/generate_contract_manifests.py

if [[ "${generated_real_bindings}" -eq 1 ]]; then
  write_binding_markers
fi

echo "Contract generation complete."
