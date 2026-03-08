from __future__ import annotations

from typing import Any, Protocol


class BrowserPage(Protocol):
    url: str

    async def goto(self, target_url: str) -> None: ...

    async def read(self, selector: str) -> str: ...

    async def extract(self, selector: str) -> dict[str, Any]: ...

    async def screenshot(self) -> bytes: ...

    async def content(self) -> str: ...

    async def close(self) -> None: ...


class BrowserSession(Protocol):
    session_ref: str
    page_ref: str

    async def new_page(self) -> BrowserPage: ...

    async def close(self) -> None: ...


class BrowserAutomationBackend(Protocol):
    async def open_session(self, *, read_only: bool) -> BrowserSession: ...

