from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from uuid import uuid4

from .errors import PlaywrightUnavailableError

try:  # pragma: no cover - exercised indirectly when dependency is installed.
    from playwright.async_api import Browser as PlaywrightBrowser
    from playwright.async_api import BrowserContext as PlaywrightBrowserContext
    from playwright.async_api import Page as PlaywrightPage
    from playwright.async_api import Playwright
    from playwright.async_api import async_playwright
except ImportError:  # pragma: no cover - default in CI/tests for this repo.
    Playwright = Any  # type: ignore[assignment]
    PlaywrightBrowser = Any  # type: ignore[assignment]
    PlaywrightBrowserContext = Any  # type: ignore[assignment]
    PlaywrightPage = Any  # type: ignore[assignment]
    async_playwright = None


@dataclass(slots=True)
class PlaywrightPageAdapter:
    page: PlaywrightPage

    @property
    def url(self) -> str:
        return self.page.url

    async def goto(self, target_url: str) -> None:
        await self.page.goto(target_url, wait_until="domcontentloaded")

    async def read(self, selector: str) -> str:
        locator = self.page.locator(selector)
        return (await locator.inner_text()).strip()

    async def extract(self, selector: str) -> dict[str, Any]:
        locator = self.page.locator(selector)
        return {
            "selector": selector,
            "text": (await locator.inner_text()).strip(),
            "html": await locator.inner_html(),
        }

    async def click(self, selector: str) -> None:
        await self.page.locator(selector).click()

    async def fill(self, selector: str, value: str) -> None:
        await self.page.locator(selector).fill(value)

    async def submit(self, selector: str) -> None:
        await self.page.locator(selector).click()

    async def screenshot(self) -> bytes:
        return await self.page.screenshot(full_page=True)

    async def content(self) -> str:
        return await self.page.content()

    async def close(self) -> None:
        await self.page.close()


@dataclass(slots=True)
class PlaywrightSessionAdapter:
    context: PlaywrightBrowserContext
    session_ref: str

    async def new_page(self) -> PlaywrightPageAdapter:
        page = await self.context.new_page()
        return PlaywrightPageAdapter(page=page)

    @property
    def page_ref(self) -> str:
        pages = getattr(self.context, "pages", [])
        if not pages:
            return "page:pending"
        return f"page:{id(pages[-1])}"

    async def close(self) -> None:
        await self.context.close()


class PlaywrightBrowserBackend:
    """Thin Playwright lifecycle wrapper for the Phase 05 browser baseline."""

    def __init__(self, *, headless: bool = True) -> None:
        self._headless = headless
        self._playwright_cm: Any = None
        self._playwright: Playwright | None = None
        self._browser: PlaywrightBrowser | None = None

    async def _ensure_browser(self) -> PlaywrightBrowser:
        if async_playwright is None:
            raise PlaywrightUnavailableError(
                "Playwright is not installed. Add the playwright package and browser binaries "
                "before using the concrete browser backend."
            )

        if self._browser is not None:
            return self._browser

        self._playwright_cm = async_playwright()
        self._playwright = await self._playwright_cm.__aenter__()
        self._browser = await self._playwright.chromium.launch(headless=self._headless)
        return self._browser

    async def open_session(self, *, read_only: bool) -> PlaywrightSessionAdapter:
        browser = await self._ensure_browser()
        context = await browser.new_context()
        return PlaywrightSessionAdapter(
            context=context,
            session_ref=f"playwright:{uuid4().hex}",
        )

    async def close(self) -> None:
        if self._browser is not None:
            await self._browser.close()
            self._browser = None
        if self._playwright_cm is not None:
            await self._playwright_cm.__aexit__(None, None, None)
            self._playwright_cm = None
            self._playwright = None
