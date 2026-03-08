# Event catalog

- `events.yaml` is the canonical event registry.
- `index.yaml` is the compact event -> schema -> version mapping.
- `schema/event-payloads/` contains one typed payload schema per event type.

Rules:
- Every event type must have an explicit payload schema.
- Session replay depends on payload schema coverage; missing coverage is a validation failure.
