# Fresh-clone first run

Use this runbook when bringing up Aegis from a fresh clone for the first time.

## Preconditions

- Python is installed and available on `PATH`
- Docker with `docker compose` is installed
- the repo has been cloned locally

## Workflow

1. run `make bootstrap`
2. run `make eval-up`
3. run `make eval-init`
4. run `make eval-check`
5. run `make smoke`

## Expected outcome

- the Python validation environment exists under `.venv`
- the evaluation stack is running
- MinIO and NATS bootstrap steps have been applied
- the dev and test Postgres databases exist
- onboarding and deployment manifests validate
- smoke validation passes without hidden manual repair steps

## Do not do this

- do not replace the evaluation stack with an undocumented local variant
- do not skip `make eval-check` when validating a fresh clone path
- do not point new engineers at missing root documents or stale setup steps
