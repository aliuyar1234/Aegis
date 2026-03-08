# aegis_gateway

## Purpose

API and operator entry surface

## Responsibilities

- authn/authz hooks
- HTTP/WS/SSE/LiveView endpoints
- must never bypass runtime APIs

## Must not own

- hidden authoritative state outside the assigned boundary
- logic that belongs to another app just because it is convenient

## First implementation note

When adding code here, link the module or boundary to the relevant phase doc, ADR, acceptance criteria, and tests.
