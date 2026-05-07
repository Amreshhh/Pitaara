import asyncio
import time
from contextlib import asynccontextmanager
from curl_cffi.requests import AsyncSession
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from live_rates import fetch_tanishq, fetch_malabar, fetch_senco, fetch_candere, print_beautiful_console

# ==========================================
# GLOBAL CACHE (Stored in RAM for entire day)
# ==========================================
GOLD_CACHE = {
    "last_updated": None,
    "rates": [],
    "cache_status": "empty"
}

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
                brands_order = ["Tanishq", "Malabar", "Senco", "Candere"]

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
    
    # 1. Run once immediately on server startup
    await fetch_and_cache_rates()
    
    # 2. Set up APScheduler for daily updates
    scheduler = AsyncIOScheduler()
    
    # Schedule to run every day at 12:00 PM (Noon)
    scheduler.add_job(fetch_and_cache_rates, 'cron', hour=12, minute=0)
    scheduler.start()
    print("📅 Scheduler activated - Daily update scheduled at 12:00 PM (Noon)")
    
    yield  # Server runs here
    
    # Clean up on shutdown
    print("\n🛑 Server Shutting Down - Stopping Scheduler...")
    scheduler.shutdown()
