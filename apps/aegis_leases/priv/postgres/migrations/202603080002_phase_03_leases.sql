CREATE TABLE IF NOT EXISTS session_leases (
  session_id TEXT PRIMARY KEY,
  tenant_id TEXT NOT NULL,
  workspace_id TEXT NOT NULL,
  owner_node TEXT NOT NULL,
  lease_epoch BIGINT NOT NULL CHECK (lease_epoch >= 1),
  lease_status TEXT NOT NULL CHECK (lease_status IN ('active', 'ambiguous', 'expired')),
  lease_expires_at TIMESTAMPTZ NOT NULL,
  last_renewed_at TIMESTAMPTZ NOT NULL,
  recovery_reason TEXT,
  inserted_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_session_leases_owner_node
  ON session_leases (owner_node);

CREATE INDEX IF NOT EXISTS idx_session_leases_status_expiry
  ON session_leases (lease_status, lease_expires_at);
