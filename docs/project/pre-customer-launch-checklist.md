# Pre-Customer Launch Checklist

## Goal

This checklist defines the bar between "strong engineering repo" and "software we can responsibly put in front of a customer."

For Aegis, the launch bar is not just feature completeness. It is proof that the runtime can be installed, operated, upgraded, recovered, secured, and supported under realistic customer conditions.

## Current repo status

The current SSOT phase remains PHASE-26.
That means the repo now has explicit, machine-checkable surfaces through PHASE-25,
plus the PHASE-26 post-GA planning surface, for:

- fresh-clone onboarding and evaluation deployment
- two canonical customer golden paths
- release signoff and launch-readiness evidence
- launch security baseline
- support severities, escalation, and customer communication surfaces
- real-infrastructure proving
- launch observability and alerting baseline
- customer environment readiness
- customer-facing operations packaging
- design-partner pilot governance and the launch go/no-go bundle
- pilot launch waves and operating cadence
- pilot control-room roles and handoffs
- customer feedback triage and issue-governance loop
- launch exception governance and containment paths
- pilot exit review and pilot-operations evidence bundle
- repeatable customer rollout and GA transition planning
- tenant-isolated production readiness and migration boundaries
- service-scale support and operations readiness
- rollout scorecards and GA transition evidence
- post-GA live customer operations and release automation planning

The checklist below remains the broader launch bar, but its remaining repo-owned
gaps are now represented as explicit PHASE-23 artifacts.
Proof in real customer or production-like infrastructure is still an execution
activity, not just a documentation claim.

## Must Have

- A fresh-clone engineer onboarding path that gets a new team member from zero to `make validate`, local startup, and one golden-path demo without tribal knowledge.
- An official deployment path for evaluation and production-like use, including documented requirements for PostgreSQL, NATS JetStream, object storage, secrets, networking, and artifact retention.
- Versioned release artifacts with clear release notes, upgrade notes, rollback notes, and supported version windows.
- At least two end-to-end customer workflows that prove the Aegis thesis:
  one read-heavy browser-backed service operation and one approval-gated effectful browser operation with replay and operator intervention.
- Backup, PITR, restore, and rollback drills that have been executed in real infrastructure and produce retained evidence.
- Rolling-upgrade proof for the supported deployment shape, including lease-safe drain/adopt behavior and no duplicate side effects.
- Baseline observability with dashboards and alerts for session ownership, replay health, checkpoint lag, outbox health, worker health, artifact upload failures, approval backlog, and degraded-mode entry.
- Defined SLOs and operational thresholds for the control plane, execution plane, and artifact path.
- Security baseline coverage:
  dependency audit, SBOM, secret scanning, signed build artifacts, hardened defaults, scoped credentials, and documented key rotation procedures.
- Tenant and workspace isolation validated in a production-like environment, not only through static repo assets.
- A documented support and incident model with severity levels, escalation paths, customer communication templates, and on-call ownership.
- Customer-facing documentation for installation, deployment, upgrades, limits, failure modes, and operational responsibilities.
- A design-partner pilot plan with success criteria, rollout scope, kill-switch conditions, and explicit non-goals.

## Current mapping

Already made explicit in repo surfaces:

- fresh-clone onboarding and official evaluation deployment
  - `docs/operations/evaluation-deployment.md`
  - `docs/runbooks/fresh-clone-first-run.md`
  - `meta/fresh-clone-onboarding.yaml`
  - `meta/evaluation-deployment-profile.yaml`
- customer golden paths
  - `docs/design-docs/customer-golden-paths.md`
  - `docs/runbooks/customer-golden-path-execution.md`
  - `meta/customer-golden-paths.yaml`
- release signoff and launch-readiness evidence
  - `docs/design-docs/release-candidate-signoff.md`
  - `docs/runbooks/release-candidate-signoff.md`
  - `meta/release-signoff-manifest.yaml`
  - `meta/launch-readiness-evidence-manifest.yaml`
  - `docs/generated/phase-22-launch-readiness-evidence.json`
- launch security baseline
  - `docs/design-docs/launch-security-baseline.md`
  - `docs/runbooks/security-baseline-review.md`
  - `meta/security-baseline-manifest.yaml`
- support model
  - `docs/design-docs/support-operating-model.md`
  - `docs/operations/support.md`
  - `docs/runbooks/support-escalation.md`
  - `docs/runbooks/customer-incident-communications.md`
  - `meta/support-model.yaml`
- real-infrastructure proving
  - `docs/design-docs/real-infrastructure-proving.md`
  - `docs/runbooks/production-like-proving.md`
  - `meta/real-infrastructure-proving.yaml`
- launch observability and alerting
  - `docs/design-docs/launch-observability-baseline.md`
  - `docs/operations/launch-observability.md`
  - `docs/runbooks/launch-observability-review.md`
  - `meta/launch-observability-baseline.yaml`
- customer environment readiness
  - `docs/design-docs/customer-environment-readiness.md`
  - `docs/operations/customer-environment-readiness.md`
  - `docs/runbooks/customer-environment-acceptance.md`
  - `meta/customer-environment-readiness.yaml`
- customer-facing operations package
  - `docs/design-docs/customer-operations-package.md`
  - `docs/operations/customer-operations.md`
  - `docs/runbooks/customer-operations-handshake.md`
  - `meta/customer-operations-package.yaml`
- design-partner pilot governance and launch decision evidence
  - `docs/design-docs/design-partner-pilot-governance.md`
  - `docs/runbooks/pilot-go-no-go.md`
  - `meta/pilot-governance-manifest.yaml`
  - `docs/generated/phase-23-launch-governance-evidence.json`
- pilot launch-wave execution
  - `docs/design-docs/pilot-launch-wave.md`
  - `docs/runbooks/pilot-launch-day.md`
  - `meta/pilot-launch-wave.yaml`
- pilot control-room operations
  - `docs/design-docs/pilot-control-room.md`
  - `docs/operations/pilot-operations.md`
  - `docs/runbooks/pilot-control-room.md`
  - `meta/pilot-control-room.yaml`
- customer feedback governance
  - `docs/design-docs/customer-feedback-governance.md`
  - `docs/runbooks/customer-feedback-triage.md`
  - `meta/customer-feedback-loop.yaml`
- launch exception governance
  - `docs/design-docs/launch-exception-governance.md`
  - `docs/runbooks/launch-exception-response.md`
  - `meta/launch-exception-governance.yaml`
- pilot exit review and pilot-operations evidence
  - `docs/design-docs/pilot-exit-review.md`
  - `docs/runbooks/pilot-exit-review.md`
  - `meta/pilot-exit-review-manifest.yaml`
  - `meta/phase24-pilot-operations-evidence-manifest.yaml`
  - `docs/generated/phase-24-pilot-operations-evidence.json`

Still broader than repo closure alone:

- proof in real customer or production-like infrastructure rather than repo-only evidence
- tenant and workspace isolation validation in production-like environments

## Should Have

- Official infrastructure automation for the supported deployment modes, such as Helm, Terraform, or equivalent install surfaces.
- A one-command or one-workflow release-candidate verification pass that bundles upgrade, restore, and phase-gate evidence into a single signoff artifact.
- A production-readiness review against the threat models, invariants, and runbooks before each customer-facing milestone.
- Fleet-level triage dashboards and evidence bundles ready for support engineers, not only core runtime engineers.
- A reference architecture package for shared, isolated-execution, and dedicated deployment tiers.
- Documented capacity guidance for expected session counts, artifact volume, and tenant isolation boundaries.
- A pilot operator training path so customer-side operators know how to inspect, pause, approve, quarantine, replay, and escalate sessions.
- A formal acceptance checklist for "customer environment is ready" covering DNS, certificates, storage, backups, alerts, and secrets handling.
- A small demo or sandbox environment that mirrors the real supported path instead of a special-case showcase stack.

## Nice To Have

- Public benchmark or conformance scorecards derived from the internal benchmark corpus.
- A polished install experience for non-expert adopters.
- Sample domain packs or reference connectors that demonstrate best-practice extension development.
- Customer-safe example datasets, traces, and replay bundles for workshops and evaluations.
- A self-serve evaluation guide for teams that want to test Aegis without direct founder/operator help.

## Exit Criteria

- A new engineer can install and validate the system from a clean environment in under one hour using only the docs.
- A new operator can run the golden-path workflows, inspect the timeline, and perform a controlled intervention using only the runbooks.
- A release candidate can prove successful upgrade, rollback, restore, and evidence generation before approval.
- The deployment has clear operational ownership, alerting, and support procedures.
- A pilot customer can run a bounded real workflow on Aegis with explicit success criteria and rollback conditions.

## Recommended Order

1. Fresh-clone onboarding and official deployment path
2. Golden customer workflows
3. Real infrastructure drills for backup, restore, upgrade, and rollback
4. Security hardening and release discipline
5. Customer-facing docs and support model
6. Design-partner pilot

## Anti-Patterns

- Do not broaden the product surface before the installation and operational path is boring.
- Do not treat repo-complete phases as equivalent to customer-ready software.
- Do not rely on founder-only knowledge for deployment, debugging, or recovery.
- Do not ship without a rollback story.
- Do not confuse impressive architecture with proven operability.
