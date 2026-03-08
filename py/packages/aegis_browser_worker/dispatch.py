from __future__ import annotations

from typing import Any

from .service import BrowserWorkerService


class BrowserDispatchHandler:
    """Thin dispatch boundary for the browser worker skeleton."""

    def __init__(self, service: BrowserWorkerService) -> None:
        self._service = service

    async def handle_dispatch(self, dispatch_input: dict[str, Any]) -> dict[str, Any]:
        return await self._service.execute_fixture(dispatch_input)
