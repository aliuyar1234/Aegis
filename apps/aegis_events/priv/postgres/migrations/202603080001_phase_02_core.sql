CREATE TABLE IF NOT EXISTS sessions (
    session_id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL,
    workspace_id TEXT NOT NULL,
    session_kind TEXT NOT NULL,
    requested_by TEXT NOT NULL,
    owner_node TEXT NOT NULL,
    last_seq_no BIGINT NOT NULL DEFAULT 0,
    last_event_hash TEXT NOT NULL DEFAULT 'genesis',
    current_checkpoint_id TEXT,
    inserted_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS session_events (
    event_id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL,
    workspace_id TEXT NOT NULL,
    session_id TEXT NOT NULL REFERENCES sessions(session_id) ON DELETE CASCADE,
    seq_no BIGINT NOT NULL,
    type TEXT NOT NULL,
    event_version INTEGER NOT NULL,
    occurred_at TIMESTAMPTZ NOT NULL,
    recorded_at TIMESTAMPTZ NOT NULL,
    actor_kind TEXT NOT NULL,
    actor_id TEXT NOT NULL,
    command_id TEXT,
    correlation_id TEXT,
    causation_id TEXT,
    trace_id TEXT,
    span_id TEXT,
    lease_epoch BIGINT NOT NULL,
    idempotency_key TEXT,
    determinism_class TEXT NOT NULL,
    prev_event_hash TEXT NOT NULL,
    event_hash TEXT NOT NULL,
    payload JSONB NOT NULL
);

CREATE UNIQUE INDEX IF NOT EXISTS session_events_session_seq_idx
    ON session_events(session_id, seq_no);

CREATE TABLE IF NOT EXISTS session_checkpoints (
    checkpoint_id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL REFERENCES sessions(session_id) ON DELETE CASCADE,
    seq_no BIGINT NOT NULL,
    payload JSONB NOT NULL,
    inserted_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS session_checkpoints_session_seq_idx
    ON session_checkpoints(session_id, seq_no DESC);

CREATE TABLE IF NOT EXISTS outbox (
    outbox_id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL REFERENCES sessions(session_id) ON DELETE CASCADE,
    event_id TEXT NOT NULL REFERENCES session_events(event_id) ON DELETE CASCADE,
    event_type TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    subject TEXT NOT NULL,
    payload JSONB NOT NULL,
    inserted_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    published_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS outbox_pending_idx
    ON outbox(status, inserted_at);
