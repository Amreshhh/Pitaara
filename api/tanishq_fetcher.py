import asyncio
import re
import time
from typing import Iterable, Optional

from curl_cffi.requests import AsyncSession
from selectolax.parser import HTMLParser

try:
    from playwright.async_api import async_playwright
except ImportError:  # pragma: no cover - dependency may be missing in local environments
    async_playwright = None


def get_no_cache_headers():
    return {
        "Cache-Control": "no-cache, no-store, must-revalidate",
        "Pragma": "no-cache",
        "Expires": "0",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    }


def _extract_numeric_price(text: str) -> Optional[int]:
    if not text:
        return None

    match = re.search(r"₹?\s*([\d,]+(?:\.\d+)?)", text)
    if not match:
        return None

    raw = match.group(1).replace(",", "")
    try:
        value = float(raw)
    except Exception:
        return None

    if not value or value <= 0:
        return None

    return int(round(value))


def _iter_candidate_nodes(tree: HTMLParser, selectors: Iterable[str]):
    for selector in selectors:
        try:
            node = tree.css_first(selector)
        except Exception:
            node = None
        if node:
            yield selector, node


def _normalize_tanishq_rate(rate: int) -> int:
    """Normalize scraped Tanishq rates to per-10g values."""
    if rate <= 0:
        return rate

    num_digits = len(str(int(rate)))
    if num_digits <= 3:
        return rate * 100
    if num_digits == 4:
        return rate * 10
    if num_digits >= 6:
        return int(round(rate / 10))

    return rate


async def fetch_tanishq(session: AsyncSession):
    print("📡 Fetching Tanishq...")
    url = f"https://www.tanishq.co.in/gold-rate.html?lang=en_IN&_ts={int(time.time())}"

    if async_playwright is None:
        raise RuntimeError("Playwright is not installed. Add playwright to requirements and install Chromium.")

    candidate_selectors = [
        "table.goldrate-table.fixedhgt.goldrate-table-22kt tbody tr:first-child td:nth-child(2)",
        "table.goldrate-table.fixedhgt.goldrate-table-22kt tbody tr:first-child td:last-child",
        "table.goldrate-table.fixedhgt.goldrate-table-22kt tbody tr:first-child",
        "table.goldrate-table.goldrate-table-22kt tbody tr:first-child td:nth-child(2)",
        "table.goldrate-table.goldrate-table-22kt tbody tr:first-child",
        "table.goldrate-table.fixedhgt.goldrate-table-24kt tbody tr:first-child td:nth-child(2)",
        "table.goldrate-table.fixedhgt.goldrate-table-24kt tbody tr:first-child",
        '[class*="goldrate-table"] tbody tr:first-child td:nth-child(2)',
    ]

    for attempt in range(3):
        try:
            rate_22k: Optional[int] = None

            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context(
                    viewport={"width": 1440, "height": 1600},
                    locale="en-US",
                    user_agent=get_no_cache_headers()["User-Agent"],
                )
                page = await context.new_page()
                try:
                    response = await page.goto(url, wait_until="domcontentloaded", timeout=45000)
                    status_code = response.status if response else None
                    if status_code == 403:
                        print(f"⛔ Tanishq blocked automated browser access with HTTP 403 on attempt {attempt + 1}")
                        return None

                    await page.wait_for_timeout(4000)

                    page_text = await page.locator("body").inner_text(timeout=10000)
                    if page_text:
                        for token in ("Access Denied", "Forbidden", "Robot", "captcha"):
                            if token.lower() in page_text.lower():
                                print(f"⛔ Tanishq browser page appears blocked: {token}")
                                return None

                    for selector in candidate_selectors:
                        locator = page.locator(selector)
                        count = await locator.count()
                        if count == 0:
                            continue

                        for index in range(min(count, 3)):
                            item = locator.nth(index)
                            texts = []
                            try:
                                texts.append(await item.inner_text())
                            except Exception:
                                pass

                            try:
                                texts.extend(await item.locator("td").all_inner_texts())
                            except Exception:
                                pass

                            for text in texts:
                                extracted = _extract_numeric_price(text)
                                if extracted:
                                    rate_22k = extracted
                                    print(f"✅ Tanishq matched selector on attempt {attempt + 1}: {selector}")
                                    break

                            if rate_22k:
                                break

                        if rate_22k:
                            break

                    if not rate_22k:
                        for pattern in (r"22\s*K[^\d]{0,20}(\d[\d,]+)", r"(\d[\d,]+)[^\d]{0,20}22\s*K"):
                            match = re.search(pattern, page_text or "", flags=re.IGNORECASE | re.DOTALL)
                            if match:
                                extracted = _extract_numeric_price(match.group(1))
                                if extracted:
                                    rate_22k = extracted
                                    print(f"✅ Tanishq matched body text pattern on attempt {attempt + 1}: {pattern}")
                                    break
                finally:
                    await browser.close()

            if not rate_22k:
                raise ValueError("No numeric rate found in candidate selectors")

            rate_22k = _normalize_tanishq_rate(rate_22k)
            rate_24k = int(round(rate_22k * (24.0 / 22.0)))
            rate_18k = int(round(rate_24k * (18.0 / 24.0)))
            rate_14k = int(round(rate_24k * (14.0 / 24.0)))

            return {
                "Brand": "Tanishq",
                "24K": rate_24k,
                "22K": rate_22k,
                "18K": rate_18k,
                "14K": rate_14k,
            }

        except Exception as e:
            status_code = getattr(getattr(e, "response", None), "status_code", None)
            if status_code == 403:
                print(f"⛔ Tanishq blocked automated access with HTTP 403 on attempt {attempt + 1}")
                return None

            print(f"⚠️ Tanishq attempt {attempt + 1} failed: {e}")
            if attempt < 2:
                await asyncio.sleep((attempt + 1) * 2)

    print("❌ Tanishq failed after 3 attempts.")
    return None