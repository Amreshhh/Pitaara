"""Scraper configuration and fallback rates.

The fallback data is refreshed automatically by the live-rate cache job and
persisted to api/live_rate_fallbacks.json. If that file is missing or invalid,
the hard-coded defaults below are used.
"""

from __future__ import annotations

import json
from pathlib import Path


DEFAULT_SCRAPER_FALLBACK_RATES = {
    "Tanishq": {
        "24K": 15200,
        "22K": 13900,
        "18K": 11400,
        "14K": 8900,
    },
    "Malabar": {
        "24K": 15100,
        "22K": 13800,
        "18K": 11300,
        "14K": 8800,
    },
    "Senco": {
        "24K": 15300,
        "22K": 14000,
        "18K": 11500,
        "14K": 8950,
    },
    "Candere": {
        "24K": 15200,
        "22K": 13900,
        "18K": 11400,
        "14K": 8900,
    },
}


def _load_fallback_rates():
    fallback_file = Path(__file__).with_name("live_rate_fallbacks.json")
    if not fallback_file.exists():
        return DEFAULT_SCRAPER_FALLBACK_RATES

    try:
        with fallback_file.open("r", encoding="utf-8") as file_handle:
            payload = json.load(file_handle)

        rates = payload.get("rates") if isinstance(payload, dict) else None
        if not isinstance(rates, dict):
            return DEFAULT_SCRAPER_FALLBACK_RATES

        normalized = {}
        for brand_name, brand_rates in rates.items():
            if not isinstance(brand_rates, dict):
                continue

            try:
                normalized[brand_name] = {
                    "24K": int(round(float(brand_rates["24K"]))),
                    "22K": int(round(float(brand_rates["22K"]))),
                    "18K": int(round(float(brand_rates["18K"]))),
                    "14K": int(round(float(brand_rates["14K"]))),
                }
            except (KeyError, TypeError, ValueError):
                continue

        return normalized or DEFAULT_SCRAPER_FALLBACK_RATES
    except (OSError, ValueError, TypeError, json.JSONDecodeError):
        return DEFAULT_SCRAPER_FALLBACK_RATES


SCRAPER_FALLBACK_RATES = _load_fallback_rates()

# Fallback rates for specific purity levels when partial scraping fails.
TANISHQ_22K_FALLBACK = SCRAPER_FALLBACK_RATES.get("Tanishq", {}).get("22K", 13900)
CANDERE_24K_FALLBACK = SCRAPER_FALLBACK_RATES.get("Candere", {}).get("24K", 15200)
