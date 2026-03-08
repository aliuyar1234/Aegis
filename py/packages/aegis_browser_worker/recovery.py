from __future__ import annotations

from datetime import UTC, datetime

from .models import BrowserHandleState, BrowserRecoveryPoint


class BrowserRecoverySerializer:
    """Produces checkpoint-friendly browser handle recovery payloads."""

    @staticmethod
    def build_recovery_point(
        *,
        handle: BrowserHandleState,
        artifact_ids: list[str],
        fixture_id: str,
    ) -> BrowserRecoveryPoint:
        stable_marker = handle.stable_page_marker or f"{handle.page_ref}:{handle.current_url}"
        restart_hint = (
            handle.restart_hint
            or f"reattach:{handle.browser_handle_id}:{handle.page_ref}:{fixture_id}"
        )
        checkpoint_handle = {
            "browser_handle_id": handle.browser_handle_id,
            "provider_kind": handle.provider_kind,
            "provider_session_ref": handle.provider_session_ref or "session:pending",
            "page_ref": handle.page_ref or "page:pending",
            "state_ref": handle.state_ref,
            "last_stable_artifact_id": handle.last_stable_artifact_id or "artifact:pending",
            "read_only_baseline_complete": handle.read_only_baseline_complete,
        }
        return BrowserRecoveryPoint(
            browser_handle=handle,
            stable_page_marker=stable_marker,
            artifact_ids=artifact_ids,
            restart_hint=restart_hint,
            checkpoint_browser_handle=checkpoint_handle,
            checkpoint_browser_handles=[checkpoint_handle],
        )

    @staticmethod
    def timestamp_now() -> str:
        return datetime.now(UTC).isoformat()
