from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import asyncio
import os
import math
import motor.motor_asyncio
from dotenv import load_dotenv
import traceback

# Live rates scraping imports
from curl_cffi.requests import AsyncSession

try:
    from live_rates import fetch_tanishq, fetch_malabar, fetch_senco, fetch_candere
    from cache_manager import lifespan, GOLD_CACHE
except ImportError:
    from api.live_rates import fetch_tanishq, fetch_malabar, fetch_senco, fetch_candere
    from api.cache_manager import lifespan, GOLD_CACHE

# Load environment variables
load_dotenv()

# 🔥 Initialize FastAPI with lifespan context manager (for cron job)
app = FastAPI(lifespan=lifespan)

# --- DATABASE SETUP ---
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)
db = client["jewelry_database"]

# --- CORS SETUP ---

# 1. Define your allowed origins here
origins = [
    "http://localhost:3000", # For your local React/Next.js testing
    "https://pitaara.vercel.app", # Replace with your LIVE frontend Vercel URL
]

# 2. Update the middleware to use the origins list
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins, # Changed from ["*"] to origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- REQUEST MODELS ---
class CalculatorRequest(BaseModel):
    weight: float
    weight_range: Optional[str] = None
    purity: str
    jewellery_type: str
    metal_type: str = "Gold"


class BrandSummaryRequest(BaseModel):
    brand: str
    weight: float
    weight_range: Optional[str] = None
    purity: str
    category: str


def _parse_weight_range(weight_range: Optional[str]):
    if not weight_range or not isinstance(weight_range, str):
        return None
    parts = weight_range.split("-")
    if len(parts) != 2:
        return None
    try:
        min_w = float(parts[0].strip())
        max_w = float(parts[1].strip())
    except (ValueError, TypeError):
        return None
    if not (math.isfinite(min_w) and math.isfinite(max_w)):
        return None
    if min_w > max_w:
        min_w, max_w = max_w, min_w
    return round(min_w, 2), round(max_w, 2)

# --- UNIFIED HELPER: Get making charge stats in (x-1) to (x+1) range with elastic expansion ---
async def get_brand_making_charges(
    brand_name: str,
    category: str,
    purity: str,
    target_weight: float,
    explicit_range: Optional[tuple] = None
):
    """
    Unified function that searches in (target_weight - 1) to (target_weight + 1) range.
    If no products found, expands to (target_weight - 2) to (target_weight + 2).
    Returns lowest making charge to be used for calculations + statistics.
    """
    collection_name = f"{brand_name.lower()}_products"
    collection = db[collection_name]
    weight_field = "net_weight"
    
    async def search_range(buffer: float = 1.0, exact_range: Optional[tuple] = None):
        """Helper to search in a specific range"""
        if exact_range:
            min_w, max_w = exact_range
        else:
            min_w = round(target_weight - buffer, 2)
            max_w = round(target_weight + buffer, 2)
        
        cursor = collection.find({
            "category": {"$regex": f"^{category}$", "$options": "i"},
            "purity": purity,
            weight_field: {"$gte": min_w, "$lte": max_w},
            "type": {"$regex": "Gold", "$options": "i"}
        })
        docs = await cursor.to_list(length=None)
        
        if not docs:
            return None, min_w, max_w
        
        making_charges = []
        best_doc_weight = None
        for doc in docs:
            raw_val = doc.get("making_charges_percentage", "0")
            try:
                if isinstance(raw_val, str):
                    clean_val = float(raw_val.replace("%", "").strip())
                else:
                    clean_val = float(raw_val)
                if not math.isfinite(clean_val):
                    continue
                making_charges.append(clean_val)

                if best_doc_weight is None or clean_val < best_doc_weight[0]:
                    weight_raw = doc.get(weight_field)
                    try:
                        w = float(weight_raw)
                    except (ValueError, TypeError):
                        w = target_weight
                    best_doc_weight = (clean_val, w)
            except (ValueError, TypeError):
                continue
        
        if not making_charges:
            return None, min_w, max_w
        
        # Calculate stats
        lowest_making = min(making_charges)
        count_with_lowest = making_charges.count(lowest_making)
        total_count = len(making_charges)
        
        return {
            "lowest_making": round(lowest_making, 2),
            "count": total_count,
            "product_count": count_with_lowest,
            "searched_min_w": min_w,
            "searched_max_w": max_w,
            "best_weight": round(best_doc_weight[1], 2) if best_doc_weight else round(target_weight, 2),
            "is_empty": False
        }, min_w, max_w
    
    if explicit_range:
        result, min_w, max_w = await search_range(exact_range=explicit_range)
        if result:
            return result
        return {
            "lowest_making": 15.0,
            "count": 0,
            "searched_min_w": min_w,
            "searched_max_w": max_w,
            "is_empty": True,
            "product_count": 0,
            "best_weight": round(target_weight, 2)
        }

    # 🔥 ELASTIC EXPANSION LOGIC
    # 1. Try ±1g range first (e.g., 19-21 for input 20)
    result, min_w, max_w = await search_range(1.0)
    if result:
        return result
    
    # 2. Try ±2g range if no products (e.g., 18-22 for input 20)
    result, min_w, max_w = await search_range(2.0)
    if result:
        return result
    
    # 3. If still nothing, return empty with expanded range
    return {
        "lowest_making": 15.0,  # Fallback
        "count": 0,
        "searched_min_w": min_w,
        "searched_max_w": max_w,
        "is_empty": True,
        "product_count": 0,
        "best_weight": round(target_weight, 2)
    }


def _parse_making_percent(raw_val):
    try:
        if isinstance(raw_val, str):
            clean_val = float(raw_val.replace("%", "").strip())
        else:
            clean_val = float(raw_val)
        if math.isfinite(clean_val):
            return clean_val
    except (ValueError, TypeError):
        return None
    return None


def _extract_sku(doc):
    for key in ["sku", "product_id", "item_code", "design_code", "code", "id"]:
        if doc.get(key):
            return str(doc.get(key))
    if doc.get("_id"):
        return str(doc.get("_id"))
    return "NA"


def _extract_product_url(doc):
    """Extract product URL from document for verification link"""
    for key in ["url", "product_url", "link", "product_link", "verification_url"]:
        if doc.get(key):
            url = str(doc.get(key)).strip()
            if url and (url.startswith("http://") or url.startswith("https://")):
                return url
    return None


async def get_brand_products_in_elastic_range(
    brand_name: str,
    category: str,
    purity: str,
    target_weight: float,
    explicit_range: Optional[tuple] = None
):
    collection_name = f"{brand_name.lower()}_products"
    collection = db[collection_name]
    weight_field = "net_weight"

    async def search_range(buffer: float):
        min_w = round(target_weight - buffer, 2)
        max_w = round(target_weight + buffer, 2)
        cursor = collection.find({
            "category": {"$regex": f"^{category}$", "$options": "i"},
            "purity": purity,
            weight_field: {"$gte": min_w, "$lte": max_w},
            "type": {"$regex": "Gold", "$options": "i"}
        })
        docs = await cursor.to_list(length=None)
        return docs, min_w, max_w

    if explicit_range:
        min_w, max_w = explicit_range
        cursor = collection.find({
            "category": {"$regex": f"^{category}$", "$options": "i"},
            "purity": purity,
            weight_field: {"$gte": min_w, "$lte": max_w},
            "type": {"$regex": "Gold", "$options": "i"}
        })
        docs = await cursor.to_list(length=None)
        return docs, min_w, max_w

    docs, min_w, max_w = await search_range(1.0)
    if docs:
        return docs, min_w, max_w

    docs, min_w, max_w = await search_range(2.0)
    return docs, min_w, max_w


# ==========================================
#               API ENDPOINTS
# ==========================================

# 1. LIVE RATES API (now returns cached data - no real-time fetching!)
@app.get("/api/live-rates")
async def get_live_rates():
    """
    Returns cached live rates.
    Cache is updated:
    - Once on server startup (immediate)
    - Daily at 12:00 PM IST (6:30 AM UTC) (via APScheduler cron job)
    - Via manual /api/cron/update-rates endpoint (Vercel cron trigger)
    
    Benefits:
    - Instant response (no scraping delays)
    - Reduced server load
    - Consistent data throughout the day
    """
    return {
        "status": "success",
        "cache_status": GOLD_CACHE["cache_status"],
        "last_updated": GOLD_CACHE["last_updated"],
        "rates": GOLD_CACHE["rates"]
    }


# CRON ENDPOINT: Manual trigger for cache update (Called by Vercel Cron)
@app.get("/api/cron/update-rates")
async def update_rates_cron():
    """
    🔄 Manual endpoint to trigger cache update.
    
    Vercel Cron automatically calls this endpoint at scheduled time.
    Schedule (IST): Daily at 12:00 PM (6:30 AM UTC)
    Schedule (UTC): 0 30 6 * * * (6:30 AM UTC = 12:00 PM IST)
    
    Can also be called manually for testing or on-demand updates.
    """
    try:
        print("\n🔄 [CRON JOB] Triggered: Updating Live Rates via Vercel Cron...")
        
        # Import the cache update function
        try:
            from cache_manager import fetch_and_cache_rates
        except ImportError:
            from api.cache_manager import fetch_and_cache_rates
        
        # Execute the cache update
        await fetch_and_cache_rates()
        
        return {
            "status": "success",
            "message": "Cache updated successfully via Cron Job",
            "last_updated": GOLD_CACHE["last_updated"],
            "cache_status": GOLD_CACHE["cache_status"],
            "rates_count": len(GOLD_CACHE.get("rates", []))
        }
    except Exception as e:
        print(f"❌ Cron job failed: {str(e)}")
        traceback.print_exc()
        return {
            "status": "error",
            "message": f"Cache update failed: {str(e)}"
        }


def _resolve_cached_rate(live_rates, purity):
    for item in live_rates:
        if not item:
            continue
        rate = item.get(purity)
        if rate is None:
            continue
        try:
            resolved = float(rate)
        except (TypeError, ValueError):
            continue
        if math.isfinite(resolved):
            return resolved
    return None

# 2. CATEGORIES API
@app.get("/api/categories")
def get_categories():
    categories = [
        { "id": "earring", "label": "Earring" },
        { "id": "bali", "label": "Bali" },
        { "id": "ring", "label": "Ring" },
        { "id": "choker", "label": "Choker" },
        { "id": "necklace", "label": "Necklace" },
        { "id": "chain", "label": "Chain" },
        { "id": "bangle", "label": "Bangle" },
        { "id": "bracelet", "label": "Bracelet" },
        { "id": "kada", "label": "Kada" },
        { "id": "coin", "label": "Coin" },
        { "id": "pendant", "label": "Pendant" },
        { "id": "mangalsutra", "label": "Mangalsutra" },
        { "id": "nose_pin", "label": "Nose Pin" },
        { "id": "nath", "label": "Nath" },
        { "id": "Hoops(a type of Bali)", "label": "Hoops(a type of Bali)" },
        { "id": "maang_tikka", "label": "Maang Tikka" },
        { "id": "watch", "label": "Watch" },
        { "id": "Coin pendant", "label": "Coin pendant" },
        { "id": "Band(Plain Ring)", "label": "Band(Plain Ring)" },
    ]
    return {
        "status": "success",
        "categories": categories
    }


# 3. BRANDS API
@app.get("/api/brands") 
def get_brands():
    return {
        "status": "success",
        "brands": ["Kalyan", "Malabar", "Senco", "Tanishq"]
    }


@app.post("/api/brand-summary")
async def get_brand_summary(req: BrandSummaryRequest):
    try:
        brand = req.brand.strip()
        if brand.lower() in ["kalyan(candere)", "kalyan/candere", "candere"]:
            brand = "Kalyan"

        parsed_range = _parse_weight_range(req.weight_range) if req.category == "coin" else None

        docs, min_w, max_w = await get_brand_products_in_elastic_range(
            brand, req.category, req.purity, req.weight, explicit_range=parsed_range
        )

        points = []
        for doc in docs:
            weight = doc.get("net_weight")
            making = _parse_making_percent(doc.get("making_charges_percentage", "0"))
            try:
                weight_val = float(weight)
            except (ValueError, TypeError):
                continue

            if not math.isfinite(weight_val) or making is None:
                continue

            points.append({
                "sku": _extract_sku(doc),
                "weight": round(weight_val, 2),
                "mc": round(making, 2),
                "verification_link": _extract_product_url(doc)
            })

        points.sort(key=lambda x: (x["mc"], abs(x["weight"] - req.weight)))
        top_5 = points[:5]

        bucket_map = {}
        for point in points:
            bucket = int(round(point["mc"]))
            bucket_map.setdefault(bucket, {"count": 0, "weights": []})
            bucket_map[bucket]["count"] += 1
            bucket_map[bucket]["weights"].append(point["weight"])

        frequency_distribution = []
        for bucket in sorted(bucket_map.keys()):
            sample_weights = sorted(bucket_map[bucket]["weights"])[:3]
            frequency_distribution.append({
                "mc_bucket": bucket,
                "count": bucket_map[bucket]["count"],
                "sample_weights": sample_weights
            })

        coin_weight_summary = []
        if req.category == "coin":
            by_weight = {}
            for point in points:
                w = point["weight"]
                by_weight.setdefault(w, []).append(point["mc"])

            for w in sorted(by_weight.keys()):
                mc_list = by_weight[w]
                coin_weight_summary.append({
                    "weight": round(w, 2),
                    "mc": round(min(mc_list), 2),
                    "count": len(mc_list)
                })

        return {
            "status": "success",
            "brand": brand,
            "target_weight": req.weight,
            "target_range": {
                "min": parsed_range[0],
                "max": parsed_range[1]
            } if parsed_range else None,
            "searched_range": {
                "min": min_w,
                "max": max_w
            },
            "total_items": len(points),
            "scatter_points": points,
            "frequency_distribution": frequency_distribution,
            "coin_weight_summary": coin_weight_summary,
            "top_5_deals": top_5
        }
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error generating brand summary: {str(e)}")

# 4. MASTER CALCULATION API (Eating the Frog!)
@app.post("/api/calculate-price")
async def calculate_price(req: CalculatorRequest):
    try:
        print(f"\n📥 INCOMING REQUEST: weight={req.weight}, purity={req.purity}, type={req.jewellery_type}, weight_range={req.weight_range}")
        
        # A. Get Live Rates (from cache)
        live_rates_response = await get_live_rates()
        live_rates = live_rates_response["rates"]

        brands_to_check = [ "Tanishq", "Kalyan", "Malabar", "Senco"]
        results = []

        # B. Loop through brands and calculate
        for brand in brands_to_check:
            # Look up live rate for specific brand and purity
            brand_rate_data = next((item for item in live_rates if item and item.get("Brand") == brand), None)
            per_gram_rate = None
            if brand_rate_data:
                raw_rate = brand_rate_data.get(req.purity)
                try:
                    per_gram_rate = float(raw_rate)
                except (TypeError, ValueError):
                    per_gram_rate = None

            if per_gram_rate is None:
                per_gram_rate = _resolve_cached_rate(live_rates, req.purity)

            if per_gram_rate is None:
                raise HTTPException(status_code=503, detail=f"No cached live rate available for purity {req.purity}")
            print(f"   {brand}: Live Rate for {req.purity} = ₹{per_gram_rate}")

            # Get Making Charges in (weight-1) to (weight+1) range with lowest making charge
            parsed_range = _parse_weight_range(req.weight_range) if req.jewellery_type == "coin" else None
            print(f"   Parsed range for {brand}: {parsed_range}")
            
            db_stats = await get_brand_making_charges(
                brand,
                req.jewellery_type,
                req.purity,
                req.weight,
                explicit_range=parsed_range
            )
            
            # 🔥 USE LOWEST MAKING CHARGE FOR CALCULATION (NOT AVERAGE)
            making_percent = db_stats["lowest_making"]

            # Mathematical Calculations (Strictly NO WASTAGE)
            # For coins, always use the min range weight; for others, use best_weight if available
            if req.jewellery_type == "coin" and parsed_range:
                calculation_weight = parsed_range[0]  # Use minimum of the range
                print(f"   {brand}: COIN MODE - using min of range: {calculation_weight}")
            else:
                calculation_weight = db_stats.get("best_weight", req.weight)
                print(f"   {brand}: NON-COIN MODE - using best_weight: {calculation_weight}")
            
            gold_value = calculation_weight * per_gram_rate
            making_charges = gold_value * (making_percent / 100)
            
            subtotal = gold_value + making_charges # Wastage is 0
            gst = subtotal * 0.03
            total_estimated_price = subtotal + gst

            # DEBUG
            print(f"\n🔍 DEBUG {brand}:")
            print(f"   Rate: {per_gram_rate}, Calc Weight: {calculation_weight}, Making %: {making_percent}")
            print(f"   Gold Value: {gold_value}, Making: {making_charges}")
            print(f"   Subtotal: {subtotal}, GST: {gst}, Total: {total_estimated_price}")
            print()

            result_obj = {
                "brand": brand,
                "per_gram_rate": per_gram_rate,
                "calculation_weight": round(calculation_weight, 2),
                "gold_value": round(gold_value, 2),
                "making_charges": round(making_charges, 2),
                "making_charges_percentage": round(making_percent, 2),
                "wastage_charges": 0, # Force set to zero
                "subtotal": round(subtotal, 2),
                "gst": round(gst, 2),
                "total_estimated_price": round(total_estimated_price, 2),
                
                # Metadata for UI
                "is_empty": db_stats.get("is_empty", False),
                "db_product_count": db_stats.get("count", 0),
                "searched_min_w": db_stats.get("searched_min_w", 0),
                "searched_max_w": db_stats.get("searched_max_w", 0),
                
                # 🔥 NEW: Lowest making charge info for display
                "lowest_making_charge_in_range": {
                    "lowest_making_charge": db_stats.get("lowest_making", 15.0),
                    "product_count": db_stats.get("product_count", 0),
                    "searched_range": f"{db_stats.get('searched_min_w', req.weight-1)}-{db_stats.get('searched_max_w', req.weight+1)}g"
                }
            }
            
            results.append(result_obj)

        # C. Sort by lowest total price
        sorted_results = sorted(results, key=lambda x: x["total_estimated_price"])

        return {
            "status": "success",
            "input_parameters": req.model_dump(), # pydantic v2 compatible
            "results": sorted_results,
            "lowest_price_brand": sorted_results[0]["brand"],
            "highest_price_brand": sorted_results[-1]["brand"]
        }

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error calculating price: {str(e)}")