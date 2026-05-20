import asyncio
import re
import time
from typing import Iterable, Optional

from curl_cffi.requests import AsyncSession
from selectolax.parser import HTMLParser


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

    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Language": "en-US,en;q=0.9",
        "Sec-Ch-Ua": '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": '"Windows"',
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Upgrade-Insecure-Requests": "1",
        **get_no_cache_headers(),
    }

    for attempt in range(3):
        try:
            response = await session.get(url, headers=headers, timeout=25)
            response.raise_for_status()

            tree = HTMLParser(response.text)
            rate_22k: Optional[int] = None

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

            for selector, node in _iter_candidate_nodes(tree, candidate_selectors):
                texts = []
                try:
                    texts.append(node.text(strip=True))
                except Exception:
                    pass

                try:
                    for td in node.css("td"):
                        texts.append(td.text(strip=True))
                except Exception:
                    pass

                for text in texts:
                    extracted = _extract_numeric_price(text)
                    if extracted:
                        rate_22k = extracted
                        break

                if rate_22k:
                    print(f"✅ Tanishq matched selector on attempt {attempt + 1}: {selector}")
                    break

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
            print(f"⚠️ Tanishq attempt {attempt + 1} failed: {e}")
            if attempt < 2:
                await asyncio.sleep((attempt + 1) * 2)

    print("❌ Tanishq failed after 3 attempts.")
    return None