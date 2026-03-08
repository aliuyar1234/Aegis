ALTER TABLE outbox
    ADD COLUMN IF NOT EXISTS headers JSONB NOT NULL DEFAULT '{}'::jsonb;

CREATE TABLE IF NOT EXISTS worker_registrations (
    worker_id TEXT PRIMARY KEY,
    worker_kind TEXT NOT NULL,
    worker_version TEXT NOT NULL,
    supported_contract_versions JSONB NOT NULL DEFAULT '[]'::jsonb,
    advertised_capacity INTEGER NOT NULL DEFAULT 0,
    available_capacity INTEGER NOT NULL DEFAULT 0,
    attributes JSONB NOT NULL DEFAULT '{}'::jsonb,
    status TEXT NOT NULL DEFAULT 'active',
    last_seen_at TIMESTAMPTZ NOT NULL,
    inserted_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS worker_registrations_kind_status_idx
    ON worker_registrations(worker_kind, status, last_seen_at DESC);

CREATE TABLE IF NOT EXISTS action_executions (
    execution_id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL,
    workspace_id TEXT NOT NULL,
    session_id TEXT NOT NULL REFERENCES sessions(session_id) ON DELETE CASCADE,
    action_id TEXT NOT NULL,
    worker_kind TEXT NOT NULL,
    worker_id TEXT,
    contract_version TEXT NOT NULL,
    dispatch_subject TEXT NOT NULL,
    trace_id TEXT,
    idempotency_key TEXT,
    isolation_tier TEXT NOT NULL,
    status TEXT NOT NULL,
    lease_epoch BIGINT NOT NULL,
    accept_deadline TIMESTAMPTZ,
    soft_deadline TIMESTAMPTZ,
    hard_deadline TIMESTAMPTZ,
    accepted_at TIMESTAMPTZ,
    last_progress_seq BIGINT NOT NULL DEFAULT 0,
    last_heartbeat_seq BIGINT NOT NULL DEFAULT 0,
    last_heartbeat_at TIMESTAMPTZ,
    cancellation_reason TEXT,
    cancellation_requested_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    failed_at TIMESTAMPTZ,
    failure_error_code TEXT,
    failure_error_class TEXT,
    retryable BOOLEAN,
    safe_to_retry BOOLEAN,
    compensation_possible BOOLEAN,
    uncertain_side_effect BOOLEAN NOT NULL DEFAULT FALSE,
    result_artifact_id TEXT,
    normalized_result JSONB,
    last_payload JSONB NOT NULL DEFAULT '{}'::jsonb,
    inserted_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(session_id, action_id)
);

ALTER TABLE action_executions
    ADD COLUMN IF NOT EXISTS tenant_id TEXT;

ALTER TABLE action_executions
    ADD COLUMN IF NOT EXISTS workspace_id TEXT;

UPDATE action_executions AS e
SET tenant_id = s.tenant_id,
    workspace_id = s.workspace_id
FROM sessions AS s
WHERE e.session_id = s.session_id
  AND (e.tenant_id IS NULL OR e.workspace_id IS NULL);

ALTER TABLE action_executions
    ALTER COLUMN tenant_id SET NOT NULL;

ALTER TABLE action_executions
    ALTER COLUMN workspace_id SET NOT NULL;

CREATE INDEX IF NOT EXISTS action_executions_status_idx
    ON action_executions(status, accept_deadline, hard_deadline);

CREATE INDEX IF NOT EXISTS action_executions_session_action_idx
    ON action_executions(session_id, action_id);

CREATE INDEX IF NOT EXISTS action_executions_scope_status_idx
    ON action_executions(tenant_id, workspace_id, status, accept_deadline, hard_deadline);
