import asyncio
import re
import time
from datetime import datetime, timedelta, timezone
from typing import Iterable, Optional

from curl_cffi.requests import AsyncSession


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


def _get_ist_date_str() -> str:
    try:
        from zoneinfo import ZoneInfo

        now = datetime.now(ZoneInfo("Asia/Kolkata"))
    except Exception:
        ist = timezone(timedelta(hours=5, minutes=30), "IST")
        now = datetime.now(ist)

    return now.strftime("%d-%m-%Y")


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
    jina_url = f"https://r.jina.ai/https://www.tanishq.co.in/gold-rate.html?lang=en_IN&_ts={int(time.time())}"
    today = _get_ist_date_str()

    for attempt in range(3):
        try:
            response = await session.get(
                jina_url,
                headers={
                    **get_no_cache_headers(),
                    "Accept": "text/plain, text/markdown;q=0.9, */*;q=0.8",
                },
                timeout=35,
            )
            response.raise_for_status()

            page_text = response.text or ""
            rate_22k: Optional[int] = None

            date_patterns = [
                rf"\|\s*{re.escape(today)}\s*\|\s*₹\s*([\d,]+(?:\.\d+)?)\s*\|",
                rf"{re.escape(today)}\s*\|\s*₹\s*([\d,]+(?:\.\d+)?)",
                rf"{re.escape(today)}.*?₹\s*([\d,]+(?:\.\d+)?)",
            ]

            for pattern in date_patterns:
                match = re.search(pattern, page_text, flags=re.IGNORECASE | re.DOTALL)
                if match:
                    extracted = _extract_numeric_price(match.group(1))
                    if extracted:
                        rate_22k = extracted
                        print(f"✅ Tanishq matched today's date row via Jina on attempt {attempt + 1}: {today}")
                        break

            if not rate_22k:
                history_block_match = re.search(
                    r"# Gold Rate History.*?(?:\n\|.*?\n)+",
                    page_text,
                    flags=re.IGNORECASE | re.DOTALL,
                )
                history_text = history_block_match.group(0) if history_block_match else page_text

                row_match = re.search(
                    rf"\|\s*{re.escape(today)}\s*\|\s*₹\s*([\d,]+(?:\.\d+)?)\s*\|",
                    history_text,
                    flags=re.IGNORECASE,
                )
                if row_match:
                    extracted = _extract_numeric_price(row_match.group(1))
                    if extracted:
                        rate_22k = extracted
                        print(f"✅ Tanishq matched today's date row in history block on attempt {attempt + 1}: {today}")

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