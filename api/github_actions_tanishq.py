import asyncio
import json
import os
import sys
import uuid
import traceback
from pathlib import Path

import requests
from curl_cffi.requests import AsyncSession

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from api.tanishq_fetcher import fetch_tanishq


async def main():
    request_id = os.getenv("TANISHQ_REQUEST_ID") or str(uuid.uuid4())
    callback_url = os.getenv("TANISHQ_CALLBACK_URL")
    callback_secret = os.getenv("TANISHQ_CALLBACK_SECRET", "")
    trigger_reason = os.getenv("TANISHQ_TRIGGER_REASON", "github-actions")

    payload = {
        "request_id": request_id,
        "status": "success",
        "message": f"Tanishq fetched via GitHub Actions ({trigger_reason})",
    }

    try:
        async with AsyncSession(impersonate="chrome124") as session:
            rate = await fetch_tanishq(session)

        if not rate:
            raise RuntimeError("Tanishq fetch returned no data")

        payload["rate"] = rate
    except Exception as error:
        print(f"❌ Tanishq scrape failed: {error!r}")
        traceback.print_exc()
        payload["status"] = "failure"
        payload["message"] = f"Tanishq fetch failed via GitHub Actions ({trigger_reason})"
        payload["error"] = str(error)

    if callback_url:
        headers = {"Content-Type": "application/json"}
        if callback_secret:
            headers["Authorization"] = f"Bearer {callback_secret}"

        def _post_callback():
            return requests.post(callback_url, headers=headers, json=payload, timeout=60)

        response = await asyncio.to_thread(_post_callback)
        response.raise_for_status()
        print(response.text)
    else:
        print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())