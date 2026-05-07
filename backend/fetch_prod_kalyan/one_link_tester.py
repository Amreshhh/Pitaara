import asyncio
import json
from datetime import datetime
from curl_cffi.requests import AsyncSession

def get_formatted_date():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

async def test_single_api_link(product_id, original_url):
    print(f"🚀 Hitting Internal Pricing API for Product ID: {product_id}...\n")
    
    # The Secret Backend API Endpoint
    # Note: Humne standard pincode (400001) aur default purity (18k) pass ki hai. 
    # Candere ka server ispar default configuration return kar dega.
    api_url = f"https://www.candere.com/JewelleryProduct/product/getCustomDesignPricing/?product_id={product_id}&pincode=400001&purity_id=18k"
    
    async with AsyncSession() as session:
        try:
            response = await session.get(api_url, impersonate="chrome110", timeout=15)
            
            if response.status_code != 200:
                print(f"[!] API Failed with status code: {response.status_code}")
                return
                
            data = response.json()
            
            # ==========================================
            # 🕵️‍♂️ EXTRACTING FROM RAW JSON
            # ==========================================
            # Weights
            gross_weight = float(data.get("total_weight", 0.0))
            stone_weight_carat = float(data.get("total_stone_weight", 0.0)) 
            
            # (1 Carat = 0.2 Grams) - E-commerce standard math
            net_weight = round(gross_weight - (stone_weight_carat * 0.2), 3) 
            if net_weight <= 0: net_weight = gross_weight
            
            # Pricing & Charges
            metal_price = float(data.get("metal_price", 0.0))
            discount_making_charge = float(data.get("discount_making_charge", 0.0))
            stone_charges = float(data.get("stone_price", 0.0))
            
            # Purity
            purity = "Unknown"
            if data.get("metal") and len(data["metal"]) > 0:
                purity = data["metal"][0].get("purity", "Unknown")
            
            # ==========================================
            # 🧠 THE MAKING CHARGE MATH
            # ==========================================
            mc_percentage_str = "0 %"
            if metal_price > 0 and discount_making_charge > 0:
                mc_pct = (discount_making_charge / metal_price) * 100
                mc_percentage_str = f"{round(mc_pct, 2)} %"
                
            # Final JSON Assembly
            final_product = {
                "Brand": "Candere (Rupees)",
                "product_url": original_url,
                "sku": data.get("sku", product_id),
                "type": "Gold (Scraped)", # Yahan utils.py ka classifier lagega production mein
                "purity": purity,
                "gross_weight": gross_weight,
                "net_weight": net_weight,
                "making_charges_percentage": mc_percentage_str,
                "stone_charges": stone_charges,
                "extraction_date": get_formatted_date(),
                "category": "Jewellery" # Yahan detect_category lagega
            }
            
            # Print the final output
            print(json.dumps(final_product, indent=4))
            
        except Exception as e:
            print(f"[!] Error fetching data: {e}")

if __name__ == "__main__":
    # Jo data aapne bheja tha
    PRODUCT_URL = "https://www.candere.com/fan-of-finesse-diamond-stud-earrings.html",
    PRODUCT_ID = "48299"
    
    import sys
    if sys.platform.startswith('win'):
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(test_single_api_link(PRODUCT_ID, PRODUCT_URL))