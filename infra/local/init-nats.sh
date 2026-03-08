#!/bin/sh
set -eu

# wait for server
for i in $(seq 1 30); do
  if nats --server nats://nats:4222 server check >/dev/null 2>&1; then
    break
  fi
  sleep 1
done

nats --server nats://nats:4222 stream add ACTIONS --subjects 'aegis.v1.command.dispatch.*' 'aegis.v1.command.cancel.*' --storage file --retention work --max-age 72h --defaults >/dev/null 2>&1 || true
nats --server nats://nats:4222 stream add WORKER_EVENTS --subjects 'aegis.v1.event.accepted.*' 'aegis.v1.event.progress.*' 'aegis.v1.event.completed.*' 'aegis.v1.event.failed.*' 'aegis.v1.event.heartbeat.*' --storage file --retention limits --max-age 72h --defaults >/dev/null 2>&1 || true
nats --server nats://nats:4222 stream add WORKER_REGISTRY --subjects 'aegis.v1.registry.register.*' 'aegis.v1.registry.heartbeat.*' --storage file --retention limits --max-age 24h --defaults >/dev/null 2>&1 || true

nats --server nats://nats:4222 consumer add ACTIONS browser-workers --filter 'aegis.v1.command.dispatch.browser' --ack explicit --deliver all --pull --defaults >/dev/null 2>&1 || true
nats --server nats://nats:4222 consumer add ACTIONS planner-workers --filter 'aegis.v1.command.dispatch.planner' --ack explicit --deliver all --pull --defaults >/dev/null 2>&1 || true
nats --server nats://nats:4222 consumer add ACTIONS tool-workers --filter 'aegis.v1.command.dispatch.tool' --ack explicit --deliver all --pull --defaults >/dev/null 2>&1 || true

nats --server nats://nats:4222 consumer add ACTIONS browser-cancel --filter 'aegis.v1.command.cancel.browser' --ack explicit --deliver all --pull --defaults >/dev/null 2>&1 || true
nats --server nats://nats:4222 consumer add ACTIONS planner-cancel --filter 'aegis.v1.command.cancel.planner' --ack explicit --deliver all --pull --defaults >/dev/null 2>&1 || true
nats --server nats://nats:4222 consumer add ACTIONS tool-cancel --filter 'aegis.v1.command.cancel.tool' --ack explicit --deliver all --pull --defaults >/dev/null 2>&1 || true

nats --server nats://nats:4222 consumer add WORKER_EVENTS runtime-worker-events --filter 'aegis.v1.event.>' --ack explicit --deliver all --pull --defaults >/dev/null 2>&1 || true
