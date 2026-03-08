# py/

Python owns execution-plane work only.

## Boundary rules

Python may:
- execute browser work
- execute planner/model-heavy actions
- call external providers
- upload artifacts
- emit progress and completion

Python may not:
- assign authoritative session order
- write canonical control-plane tables
- self-approve dangerous actions
- become a hidden source of truth
