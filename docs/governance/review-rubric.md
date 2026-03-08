# Review Rubric

Use this rubric in code review, design review, and phase completion review.

## Core questions

### Runtime truth
- Does this preserve the single authoritative owner model?
- Does this keep authoritative state in the control plane?
- Does this maintain append-only session history?

### Recovery
- What happens if the worker crashes here?
- What happens if the owner node dies here?
- What happens if the datastore is unavailable here?
- Is uncertainty explicit?

### Operator trust
- Can an operator see this event or transition?
- Can an operator approve/deny/intervene where appropriate?
- Is the replay story still honest?

### Security and governance
- Does this bypass policy?
- Are dangerous actions scoped and attributable?
- Is tenant context preserved?
- Are secrets or sensitive data leaking into the wrong layer?

### Hygiene
- Did the relevant docs change?
- Did the traceability metadata change?
- Are the right tests present?
- Did we add accidental abstraction or incidental complexity?

## Review outcome language

- **Accept** — aligned and sufficiently verified
- **Accept with follow-up** — safe, but requires tracked cleanup in `../project/tech-debt.md`
- **Needs redesign** — violates thesis, drift rules, or safety model
