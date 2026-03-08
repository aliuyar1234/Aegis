# aegis_artifacts

## Purpose

Artifact metadata and signed URL orchestration

## Responsibilities

- artifact records
- retention and redaction hooks
- never stores blobs inline in events

## Must not own

- hidden authoritative state outside the assigned boundary
- logic that belongs to another app just because it is convenient

## First implementation note

When adding code here, link the module or boundary to the relevant phase doc, ADR, acceptance criteria, and tests.
