# aegis_core

## Purpose

Shared domain primitives

## Responsibilities

- core types and shared domain utilities
- no ownership of persistence, transport, or UI

## Must not own

- hidden authoritative state outside the assigned boundary
- logic that belongs to another app just because it is convenient

## First implementation note

When adding code here, link the module or boundary to the relevant phase doc, ADR, acceptance criteria, and tests.
