# Storage model

## Canonical store

PostgreSQL is the canonical system of record.

## Core tables

- `tenants`
- `workspaces`
- `sessions`
- `session_leases`
- `session_events`
- `session_checkpoints`
- `action_executions`
- `approval_requests`
- `artifacts`
- `worker_registrations`
- `outbox_messages`
- `projected_session_views`
- `schema_versions`

## sessions

Stores current coarse projection for admission and query efficiency:
- tenant/workspace ids
- isolation tier
- lifecycle fields
- latest checkpoint pointer
- latest seq_no
- current owner and lease epoch
- summary view fields

This is not a substitute for the timeline.

Phase 09 admission currently derives live-session counts from `sessions` plus the
latest terminal event state rather than maintaining a separate quota counter
table. Dedicated counters remain an optimization path if admission hot spots
need it later.

## session_events

Append-only authoritative timeline.

Design notes:
- partition by time once volume demands it
- envelope fields as real columns
- `payload` as `jsonb`
- unique `(session_id, seq_no)`
- integrity hashes per event
- no in-place mutation

## session_checkpoints

Stores structured snapshots:
- `checkpoint_id`
- `session_id`
- `seq_no`
- `checkpoint_version`
- `payload_json`
- optional artifact ref for oversized sections

Checkpoints must stay inspectable by humans and tooling.

## session_leases

Stores ownership:
- `session_id`
- `owner_node`
- `lease_epoch`
- `lease_expires_at`
- `status`

The lease table is authoritative for live ownership, not cluster presence.

## outbox_messages

Stores committed intent to publish or dispatch. This table is the glue between Postgres truth and JetStream transport.

## Artifacts

Artifacts are stored in object storage and indexed in `artifacts`.

Metadata includes:
- tenant/workspace/session linkage
- artifact kind
- hash
- size
- content type
- encryption key id
- redaction state
- retention class
- uploader identity
- storage location

## Search and indexing

v1:
- Postgres full-text on summaries, notes, and selected metadata
- trigram search for operator usability

Not v1:
- full raw-event indexing
- generalized analytics warehouse on the critical path

## Analytics separation

Operational correctness lives in Postgres.

Analytics later belong in:
- ClickHouse
- warehouse export
- cold event archive queries

Do not let BI needs shape canonical runtime tables.

## Retention and archival

Recommended policy classes:
- hot operational events
- long-lived audit events
- short-lived debug artifacts
- long-lived customer artifacts
- redacted / hidden payloads

Archive by partition and artifact policy. Never let retention policy silently rewrite timeline history; use redaction and archive metadata instead.

## Backup and integrity

Backups must support:
- point-in-time recovery for Postgres
- object-store durability checks
- event integrity scans
- replay rehearsal from backups

## Multi-tenant storage posture

Default:
- shared schema with tenant/workspace columns
- tenant-aware indexes and query guards

Higher tiers:
- dedicated object-store prefixes
- dedicated execution pools
- optional dedicated database/control-plane deployment
