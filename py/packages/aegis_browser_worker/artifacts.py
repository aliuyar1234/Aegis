from __future__ import annotations

import hashlib
from dataclasses import asdict
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from .models import ArtifactRecord, ArtifactUploadTarget, WorkerExecutionContext


class BrowserArtifactStore:
    """Generates immutable browser artifact metadata and signed-upload descriptors."""

    _CONTENT_TYPES = {
        "screenshot": "image/png",
        "pre_write_screenshot": "image/png",
        "post_write_screenshot": "image/png",
        "dom_snapshot": "text/html",
        "trace": "application/zip",
    }

    def __init__(self, *, bucket: str = "aegis-artifacts") -> None:
        self._bucket = bucket

    def register_bytes(
        self,
        *,
        context: WorkerExecutionContext,
        artifact_kind: str,
        payload: bytes,
        created_at: str | None = None,
    ) -> ArtifactRecord:
        timestamp = created_at or datetime.now(UTC).isoformat()
        artifact_id = f"artifact-{uuid4().hex}"
        sha256 = hashlib.sha256(payload).hexdigest()
        object_key = "/".join(
            [
                context.tenant_id,
                context.workspace_id,
                context.session_id,
                artifact_kind,
                f"{artifact_id}.{self._suffix_for(artifact_kind)}",
            ]
        )
        upload_target = ArtifactUploadTarget(
            method="PUT",
            url=f"https://object-store.local/{self._bucket}/{object_key}?signed=true",
            headers={
                "content-type": self._content_type_for(artifact_kind),
                "x-aegis-artifact-sha256": sha256,
            },
        )
        return ArtifactRecord(
            artifact_id=artifact_id,
            tenant_id=context.tenant_id,
            workspace_id=context.workspace_id,
            session_id=context.session_id,
            action_id=context.action_id,
            artifact_kind=artifact_kind,
            sha256=sha256,
            content_type=self._content_type_for(artifact_kind),
            size_bytes=len(payload),
            retention_class=self._retention_class_for(artifact_kind),
            redaction_state="not_requested",
            object_key=object_key,
            created_at=timestamp,
            upload_target=upload_target,
            storage_ref=f"s3://{self._bucket}/{object_key}",
        )

    @staticmethod
    def to_metadata_payload(record: ArtifactRecord) -> dict[str, Any]:
        payload = asdict(record)
        payload.pop("upload_target", None)
        payload.pop("storage_ref", None)
        return payload

    @staticmethod
    def to_event_payload(record: ArtifactRecord) -> dict[str, Any]:
        return {
            "artifact_id": record.artifact_id,
            "artifact_kind": record.artifact_kind,
            "sha256": record.sha256,
            "content_type": record.content_type,
            "size_bytes": record.size_bytes,
            "retention_class": record.retention_class,
            "redaction_state": record.redaction_state,
            "storage_ref": record.storage_ref,
            "recorded_at": record.created_at,
            "action_id": record.action_id,
        }

    def _content_type_for(self, artifact_kind: str) -> str:
        return self._CONTENT_TYPES.get(artifact_kind, "application/octet-stream")

    def _retention_class_for(self, artifact_kind: str) -> str:
        if artifact_kind == "trace":
            return "debug_short_lived"
        return "customer_operational"

    def _suffix_for(self, artifact_kind: str) -> str:
        return {
            "screenshot": "png",
            "pre_write_screenshot": "png",
            "post_write_screenshot": "png",
            "dom_snapshot": "html",
            "trace": "zip",
        }.get(artifact_kind, "bin")
