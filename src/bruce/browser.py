from __future__ import annotations

import json
import urllib.parse
import urllib.request


class BrowserUnavailable(RuntimeError):
    pass


class BrowserSkill:
    """Optional Playwright browser skill. It requires explicit installation and approval upstream."""

    def __init__(self, headless: bool = False):
        try:
            from playwright.sync_api import sync_playwright
        except ImportError as exc:
            raise BrowserUnavailable("Install browser support with: pip install -e '.[browser]' and playwright install chromium") from exc
        self._pw = sync_playwright().start()
        self.browser = self._pw.chromium.launch(headless=headless)
        self.page = self.browser.new_page()

    def open(self, url: str) -> str:
        if not url.startswith(("https://", "http://")):
            raise ValueError("Browser navigation requires an http or https URL")
        response = self.page.goto(url, wait_until="domcontentloaded", timeout=30000)
        return json.dumps({"url": self.page.url, "title": self.page.title(), "status": response.status if response else None})

    def extract_text(self, selector: str = "body") -> str:
        return self.page.locator(selector).inner_text(timeout=10000)[:50000]

    def close(self) -> None:
        self.browser.close()
        self._pw.stop()
