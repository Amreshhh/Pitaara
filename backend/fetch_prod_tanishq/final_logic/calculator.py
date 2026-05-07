import re
from live_rates import get_live_22k_rate  # 🚀 NAYA: Rate fetcher idhar hi bula liya

# 🧠 GLOBAL IN-MEMORY CACHE
# Script start hone par yeh None rahega. Ek baar fetch hone ke baad yeh rate store kar lega.
_CACHED_22K_RATE = None

def generate_dynamic_rates(rate_22k):
    """Ek 22K rate se baaki saare rates generate karta hai formula lagakar."""
    return {
        24: (round(rate_22k * (24 / 22)+1)),
        22: rate_22k,
        18: (round(rate_22k * (18 / 22)+1)),
        14: (round(rate_22k * (14 / 22)+1))
    }

def calculate_making_charges_percentage(final_price, weight, purity_str="22 Karat"):
    """
    Final Bill Price, Weight aur Purity lekar exact Making Charge % nikalta hai.
    Rate fetch aur cache karne ki zimmedari ab iski khud ki hai.
    """
    global _CACHED_22K_RATE

    # ==========================================
    # 🚀 SMART CACHING LOGIC
    # ==========================================
    if _CACHED_22K_RATE is None:
        print("⏳ [Cache Miss] Fetching Live Gold Rate for the first time...")
        rate = get_live_22k_rate()
        if rate:
            _CACHED_22K_RATE = rate/10
            print(f"🔒 [Cache Locked] 22K Rate set to ₹ {_CACHED_22K_RATE} for this session.\n")
        else:
            # Agar network error aaye toh script fail na ho, ek default rate le le
            print("⚠️ Live fetch failed! Using Fallback Rate of ₹ 14160")
            _CACHED_22K_RATE = 14160

    # Cache se rate uthao
    live_22k_rate = _CACHED_22K_RATE

    # ==========================================
    # MATHEMATICAL CALCULATIONS
    # ==========================================
    dynamic_rates = generate_dynamic_rates(live_22k_rate)
    
    purity_val = 22 # Default
    match = re.search(r'(\d+)', str(purity_str))
    if match:
        purity_val = int(match.group(1))
        
    gold_rate = dynamic_rates.get(purity_val, dynamic_rates[22])
    base_price = final_price / 1.03
    gold_value = weight * gold_rate
    making_charge_rs = base_price - gold_value

    if gold_value > 0:
        making_charges_percentage = (making_charge_rs / gold_value) * 100
    else:
        making_charges_percentage = 0

    return {
        "purity_detected": f"{purity_val}K",
        "gold_rate_used": gold_rate,
        "base_price_without_gst": round(base_price, 2),
        "gold_value": round(gold_value, 2),
        "making_charge_rs": round(making_charge_rs, 2),
        "making_charges_percentage": round(making_charges_percentage, 2)
    }

if __name__ == "__main__":
    # Test caching (Dono calls mein sirf ek baar 'Fetching' print hoga)
    print(calculate_making_charges_percentage(45000, 5.0, "22 Karat"))
    print(calculate_making_charges_percentage(35000, 4.0, "18 Karat"))