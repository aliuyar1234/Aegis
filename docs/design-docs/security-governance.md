# Security and governance model

This document defines the implementation-level trust model for Aegis.

## Machine-readable sources

- roles: `meta/rbac-roles.yaml`
- attributes: `meta/abac-attributes.yaml`
- dangerous action classes: `meta/dangerous-action-classes.yaml`
- failure/runbook mapping: `meta/failure-runbooks.yaml`
- capability-token claims: `schema/jsonschema/capability-token-claims.schema.json`
- approval request shape: `schema/jsonschema/approval-request.schema.json`

## Rules

- capability tokens are required for effectful actions
- dangerous browser writes default to `allow_with_constraints`, `require_approval`, or `deny` based on the machine-readable dangerous-action class
- worker payloads are least-privilege and may not contain broad tenant secrets
- audit and redaction events are first-class runtime artifacts, not compliance afterthoughts
