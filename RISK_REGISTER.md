# RISK_REGISTER.md

| Risk ID | Risk | Why it matters | Phase pressure point | Mitigation |
|---|---|---|---|---|
| R-001 | Elixir becomes a thin wrapper around Python | Destroys the central thesis and makes the runtime incidental | 01–05 | Keep authoritative state, leases, replay, policy, and operator control in Elixir only |
| R-002 | Split-brain session ownership | Leads to duplicate side effects and broken trust | 03, 08 | Lease epochs, self-fencing, stale-owner rejection, adoption tests |
| R-003 | Event stream becomes too noisy | Makes replay expensive and timelines unreadable | 02, 05 | Keep event stream semantically meaningful; push bulk detail to artifacts/metrics |
| R-004 | Browser wedge proves too brittle | Could undermine confidence in the whole project | 05, 08 | Start with controlled workflows, resumable handles, explicit uncertainty model |
| R-005 | Hidden authority leaks into workers | Breaks recovery and audit model | 04, 05 | Contract boundaries, DB write prohibition, code review rubric |
| R-006 | Approvals are vague or weak | Ruins enterprise trust | 07 | Bind approval to action hash and lease epoch; render exact payloads in UI |
| R-007 | Replay is not believable | Operators and recruiters stop trusting the system story | 02, 06, 08 | Historical replay from recorded outputs and artifacts, not re-execution |
| R-008 | Repo drifts away from architecture | Future Codex runs become incoherent | 00+ | Validators, ADR discipline, traceability, change policy, quality rubric |
| R-009 | Multitenancy is bolted on late | Enterprise path becomes expensive and risky | 09 | Carry tenant/workspace identity everywhere from the beginning |
| R-010 | Public demo overclaims reliability | Short-term demo success causes long-term trust damage | 08 | Use explicit uncertain-side-effect language and runbook-backed demos |
| R-011 | Postgres becomes an early bottleneck | Correctness path becomes hard to scale | 02, 08, 09 | Partition events, separate analytics, control event granularity, add quotas |
| R-012 | Build order collapses into parallel chaos | Strong team wastes time on work that the architecture has not unlocked | all | Follow phase docs and task graph; use prompts/ and `make next-tasks` |
