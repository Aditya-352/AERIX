from __future__ import annotations
import asyncio
from playwright.async_api import async_playwright
from config.settings import settings

async def fetch_page(url: str) -> tuple[str, str]:
    async with async_playwright() as p:
        browser=await p.chromium.launch(headless=True)
        try:
            page=await browser.new_page(user_agent=settings.user_agent)
            await page.goto(url, wait_until="domcontentloaded", timeout=settings.request_timeout_ms)
            await page.wait_for_timeout(1200)
            title=await page.title()
            text=await page.locator("body").inner_text()
            return title,text
        finally:
            await browser.close()
