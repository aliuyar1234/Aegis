from __future__ import annotations

from typing import Any

from .dispatch import BrowserDispatchHandler
from .service import BrowserWorkerService


class BrowserWorker:
    """Phase 05 browser worker facade over registration and dispatch handling."""

    def __init__(self, *, dispatch_handler: BrowserDispatchHandler, service: BrowserWorkerService) -> None:
        self._dispatch_handler = dispatch_handler
        self._service = service

    def registration_payload(self) -> dict[str, Any]:
        return self._service.registration_payload()

    async def handle_dispatch(self, dispatch_input: dict[str, Any]) -> dict[str, Any]:
        return await self._dispatch_handler.handle_dispatch(dispatch_input)
