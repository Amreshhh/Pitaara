import asyncio
import json
from pathlib import Path
import time
from contextlib import asynccontextmanager
from curl_cffi.requests import AsyncSession
from apscheduler.schedulers.asyncio import AsyncIOScheduler

try:
    from live_rates import fetch_tanishq, fetch_malabar, fetch_senco, fetch_candere, print_beautiful_console
except ImportError:
    from api.live_rates import fetch_tanishq, fetch_malabar, fetch_senco, fetch_candere, print_beautiful_console

# ==========================================
# GLOBAL CACHE (Stored in RAM for entire day)
# ==========================================
GOLD_CACHE = {
    "last_updated": None,
    "rates": [],
    "cache_status": "empty"
}


def _persist_fallback_rates(rates):
    """Persist fetched rates to JSON file for use as fallback on API failure."""
    fallback_file = Path(__file__).with_name("live_rate_fallbacks.json")
    payload = {"updated_at": time.strftime("%Y-%m-%d %H:%M:%S"), "rates": {}}

    for rate in rates or []:
        if not rate:
            continue

        brand_name = rate.get("Brand")
        # FIX-1: Keep original brand name (don't convert Kalyan→Candere)
        # Conversion happens when loading from file in scraper_config.py
        
        if not brand_name:
            continue

        try:
            payload["rates"][brand_name] = {
                "24K": int(round(float(rate.get("24K", 0)))),
                "22K": int(round(float(rate.get("22K", 0)))),
                "18K": int(round(float(rate.get("18K", 0)))),
                "14K": int(round(float(rate.get("14K", 0)))),
            }
        except (TypeError, ValueError):
            continue

    if not payload["rates"]:
        print("⚠️  No valid rates to persist")
        return

    try:
        # Write the file
        fallback_file.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        
        # FIX-2: Verify file was actually written successfully
        verify_data = json.loads(fallback_file.read_text(encoding="utf-8"))
        written_brands = len(verify_data.get("rates", {}))
        written_timestamp = verify_data.get("updated_at")
        print(f"✅ Persisted {written_brands} brand rates to {fallback_file}")
        print(f"   Last updated: {written_timestamp}")
        
    except (OSError, json.JSONDecodeError) as error:
        print(f"❌ Failed to persist fallback rates: {error}")

# ==========================================
# CACHE UPDATE FUNCTION (Called by cron job)
# ==========================================
async def fetch_and_cache_rates():
    """
    Fetch live rates from all brands and store in GOLD_CACHE.
    This is called:
    1. Once on server startup (to populate cache)
    2. Daily at 12:00 PM (via APScheduler cron job)
    """
    print("\n⏳ Running Scheduled Gold Rate Update...")
    try:
            async with AsyncSession(impersonate="chrome124") as session:
                tasks = [
                    fetch_tanishq(session), 
                    fetch_malabar(session), 
                    fetch_senco(session), 
                    fetch_candere(session)
                ]
                # Use return_exceptions=True so one failing scraper doesn't abort the whole batch
                results = await asyncio.gather(*tasks, return_exceptions=True)

                # Map results by brand where available
                fetched_map = {}
                for res in results:
                    if isinstance(res, Exception):
                        # log exception
                        print(f"⚠️ Scraper exception: {res}")
                        continue
                    if not res:
                        continue
                    brand_name = res.get("Brand")
                    if brand_name:
                        fetched_map[brand_name] = res

                # Brands we expect (preserve ordering)
                brands_order = ["Tanishq", "Malabar", "Senco", "Kalyan"]

                # Build new_rates preserving prior cached entries for brands that failed
                prior_rates = { (r.get("Brand") if r else None): r for r in GOLD_CACHE.get("rates", []) }
                new_rates = []
                for b in brands_order:
                    if b in fetched_map:
                        new_rates.append(fetched_map[b])
                    else:
                        # Use cached entry if available
                        if prior_rates.get(b):
                            print(f"ℹ️ Using cached rate for {b} (fetch failed)")
                            new_rates.append(prior_rates.get(b))
                        else:
                            print(f"⚠️ No data for {b} and no prior cache available; skipping")

                # Display results in console (beautiful formatting)
                if new_rates:
                    print_beautiful_console(new_rates)

                # Update RAM cache
                GOLD_CACHE["rates"] = new_rates
                GOLD_CACHE["last_updated"] = time.strftime("%Y-%m-%d %H:%M:%S")
                GOLD_CACHE["cache_status"] = "active"
                _persist_fallback_rates(new_rates)
                print("✅ Cache successfully updated!")
            
    except Exception as e:
        print(f"❌ Error updating cache: {str(e)}")
        GOLD_CACHE["cache_status"] = "error"

# ==========================================
# FASTAPI LIFESPAN MANAGER (for startup/shutdown)
# ==========================================
@asynccontextmanager
async def lifespan(app):
    """
    Lifespan context manager for FastAPI.
    - On startup: Fetch and cache rates immediately
    - Run scheduler: Cron job for daily updates
    - On shutdown: Stop scheduler
    """
    print("\n🚀 Server Starting - Initializing Live Rates Cache...")
    
    # FIX-3: Ensure fallback file exists on startup
    fallback_file = Path(__file__).with_name("live_rate_fallbacks.json")
    if not fallback_file.exists():
        try:
            from scraper_config import SCRAPER_FALLBACK_RATES
            initial_payload = {
                "updated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                "rates": SCRAPER_FALLBACK_RATES
            }
            fallback_file.write_text(json.dumps(initial_payload, indent=2), encoding="utf-8")
            print(f"✅ Created initial fallback rates file")
        except Exception as e:
            print(f"⚠️  Could not create initial fallback file: {e}")
    
    # 1. Run once immediately on server startup
    await fetch_and_cache_rates()
    
    # 2. If cache is still empty (all scrapers failed), use fallback rates
    if not GOLD_CACHE.get("rates"):
        print("\n⚠️  WARNING: All live rate scrapers failed!")
        print("💾 Using fallback rates instead...")
        
        try:
            from scraper_config import SCRAPER_FALLBACK_RATES
        except ImportError:
            from api.scraper_config import SCRAPER_FALLBACK_RATES
        
        # Convert fallback rates to API format
        rates_list = []
        for brand_name, rates in SCRAPER_FALLBACK_RATES.items():
            display_brand = "Kalyan" if brand_name == "Candere" else brand_name
            rates_list.append({
                "Brand": display_brand,
                "24K": rates.get("24K", 0),
                "22K": rates.get("22K", 0),
                "18K": rates.get("18K", 0),
                "14K": rates.get("14K", 0),
            })
        
        GOLD_CACHE["rates"] = rates_list
        GOLD_CACHE["cache_status"] = "fallback"
        print(f"   ✅ Loaded {len(rates_list)} brands from fallback rates")
        print_beautiful_console(rates_list)
    
    # 3. Set up APScheduler for daily updates
    scheduler = AsyncIOScheduler()
    
    # Schedule to run every day at 12:00 PM server time.
    # Vercel uses the separate cron trigger in api/vercel.json.
    scheduler.add_job(fetch_and_cache_rates, 'cron', hour=12, minute=0)
    scheduler.start()
    print("📅 Scheduler activated - Daily update scheduled at 12:00 PM server time")
    
    yield  # Server runs here
    
    # Clean up on shutdown
    print("\n🛑 Server Shutting Down - Stopping Scheduler...")
    scheduler.shutdown()
