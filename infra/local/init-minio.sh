#!/bin/sh
set -eu

for i in $(seq 1 30); do
  if mc ls local >/dev/null 2>&1; then
    break
  fi
  sleep 1
done

mc mb --ignore-existing local/aegis-artifacts >/dev/null 2>&1 || true
mc anonymous set none local/aegis-artifacts >/dev/null 2>&1 || true
