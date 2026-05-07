import json
import asyncio
import os
import sys
from datetime import datetime
from curl_cffi.requests import AsyncSession
from tqdm.asyncio import tqdm  # 🚀 Progress bar smoothly chalane ke liye

# ==========================================
# 🚀 UNIVERSAL UTILS INTEGRATION
# ==========================================
# Ye automatically 3 folders peeche jaakar utils ko dhoondhega 
# (Script -> logic_final -> fetch_prod_malabar -> root_path)
root_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

if root_path not in sys.path:
    sys.path.append(root_path)

from utils import detect_category, get_formatted_date, check_if_diamond 

# =========================================================
# 🛠️ HELPER FUNCTIONS (No Changes Here)
# =========================================================
def parse_malabar_number(json_str):
    if not json_str: return 0.0
    try:
        obj = json.loads(json_str)
        total_sum = 0.0
        for key, value in obj.items():
            if isinstance(value, dict):
                for sub_key, sub_value in value.items():
                    total_sum += float(sub_value) if sub_value else 0.0
            else:
                total_sum += float(value) if value else 0.0
        return total_sum
    except Exception: return 0.0

def parse_malabar_purity(json_str):
    if not json_str: return "Unknown"
    try:
        obj = json.loads(json_str)
        val = list(obj.values())[0]
        return str(val).upper() if val else "Unknown"
    except Exception: return "Unknown"

# =========================================================
# 🚀 ASYNC CORE API FETCHER
# =========================================================
async def fetch_product_breakup_async(session, sku_code, product_url, semaphore):
    api_url = 'https://www.malabargoldanddiamonds.com/graphql-magento'

    graphql_query = """
    query products($filter: ProductAttributeFilterInput) {
      products(filter: $filter) {
        items {
          name
          sku
          price_breakup { purity net_weight gross_weight metal_charges diamond_charges stone_charges making_charges tax total }
        }
      }
    }
    """

    variables_dict = {"filter": {"sku": { "eq": sku_code }}}
    params = {
        "query": graphql_query,
        "variables": json.dumps(variables_dict)
    }

    async with semaphore:
        try:
            response = await session.get(
                api_url, 
                params=params, 
                impersonate="chrome120", 
                timeout=25
            )

            if response.status_code != 200: return None
            if "html" in response.text[:20].lower() or "cloudflare" in response.text.lower(): return None

            data = response.json()
            if "errors" in data: return None
            
            items = data.get("data", {}).get("products", {}).get("items", [])
            if not items: return None
                
            item = items[0]
            breakup = item.get("price_breakup")

            if not breakup and item.get("variants"):
                variant_product = item["variants"][0].get("product", {})
                breakup = variant_product.get("price_breakup")
                
            if not breakup: return None
            
            raw_purity = breakup.get("purity", "")
            clean_purity = json.loads(raw_purity).get("Gold", "").upper() if raw_purity else "Unknown"
            
            raw_metal = breakup.get("metal_charges", "")
            gold_value = float(json.loads(raw_metal).get("Gold", 0)) if raw_metal else 0.0
            
            raw_making = breakup.get("making_charges", "")
            making_charge = float(json.loads(raw_making).get("Gold", 0)) if raw_making else 0.0
            
            mc_percent = 0
            if gold_value > 0:
                mc_percent = round((making_charge / gold_value) * 100, 2)

            product_name = item.get("name", "")
            is_stone_diamond = False

            if "diamond" in product_name.lower() or "stone" in product_name.lower():
                is_stone_diamond = True
            else:
                raw_diamond = breakup.get("diamond_charges", "")
                raw_stone = breakup.get("stone_charges", "")
                try:
                    if raw_diamond and json.loads(raw_diamond).get("loosediamond", {}).get("total_diamond_value", 0) > 0:
                        is_stone_diamond = True
                    elif raw_stone and json.loads(raw_stone).get("stone", {}).get("total_stone_value", 0) > 0:
                        is_stone_diamond = True
                except:
                    pass

            final_type = "Stone/Diamond (API Hit)" if is_stone_diamond else "Pure Gold"
            final_category = detect_category(product_name)

            final_output = {
                "Brand": "Malabar Gold & Diamonds",
                "product_url": product_url, 
                "sku": item.get("sku"),
                "type": final_type, 
                "purity": clean_purity,
                "net_weight": float(breakup.get("net_weight", 0)), 
                "making_charges_percentage": f"{mc_percent} %",
                "category": final_category,
                "extraction_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S") 
            }
            
            return final_output

        except Exception as e:
            return None

# =========================================================
# 🚀 THE MASTER CONTINUOUS PROCESSING LOOP
# =========================================================
async def process_bulk_links_async():
    input_file = "malabar_async_links.json"
    output_file = "malabar_final_data.json"
    
    print(f"\n📂 Loading links from {input_file}...")
    try:
        with open(input_file, "r", encoding="utf-8") as f:
            links_data = json.load(f)
    except FileNotFoundError:
        print(f"❌ Error: File '{input_file}' not found.")
        return

    # 🚀 Auto-Resume Logic
    final_master_data = []
    scraped_skus = set()
    
    if os.path.exists(output_file):
        try:
            with open(output_file, "r", encoding="utf-8") as f:
                content = f.read()
                if content.strip():
                    final_master_data = json.loads(content)
                    scraped_skus = {item.get("sku") for item in final_master_data if item.get("sku")}
            print(f"🔄 Found {len(scraped_skus)} already scraped items. Resuming where left off...")
        except json.JSONDecodeError:
            print(f"⚠️ Warning: Output file corrupt hai, fresh start kar rahe hain.")

    pending_links = [link for link in links_data if link.get("sku") not in scraped_skus]
    total_items = len(pending_links)

    if total_items == 0:
        print("🎉 Saara data pehle hi fetch ho chuka hai! You are 100% done.")
        return

    print(f"🎯 Found {total_items} pending products to process.\n")
    
    # ⚙️ CONCURRENCY CONFIGURATION
    CONCURRENCY = 50  # Ek waqt par 50 links chalenge. WAF rokne lage toh 30 kar dena.
    semaphore = asyncio.Semaphore(CONCURRENCY)
    
    headers = {
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Referer": "https://www.malabargoldanddiamonds.com/",
        "Origin": "https://www.malabargoldanddiamonds.com",
    }

    async with AsyncSession(headers=headers) as session:
        # 1. Saare tasks ek sath list mein daal diye
        tasks = []
        for item in pending_links:
            sku = item.get("sku")
            url = item.get("product_url")
            if sku:
                tasks.append(fetch_product_breakup_async(session, sku, url, semaphore))
        
        # 2. Continuous Execution with Smooth TQDM Progress Bar
        with tqdm(total=total_items, desc="Fetching Products", unit="item", colour="green") as pbar:
            try:
                # asyncio.as_completed turant yield karta hai jaise hi koi bhi 1 task khatam hota hai
                for future in asyncio.as_completed(tasks):
                    result = await future
                    if result:
                        final_master_data.append(result)
                    
                    # Bar ko 1 item aage badhao
                    pbar.update(1)
                    
                    # 💾 LIVE DATA STORING: Har 50 item complete hone par save maar do
                    if pbar.n % 50 == 0:
                        with open(output_file, "w", encoding="utf-8") as f:
                            json.dump(final_master_data, f, indent=4)
                            
            except KeyboardInterrupt:
                print("\n🛑 Stopped by User. Progress save kar rahe hain...")
            
            finally:
                # 💾 Final Save: Script rukne par ya khatam hone par final save lazmi hai
                with open(output_file, "w", encoding="utf-8") as f:
                    json.dump(final_master_data, f, indent=4)

    print("\n" + "="*60)
    print(f"🎉 ASYNC PIPELINE COMPLETE! Scraped {len(final_master_data)} total products.")
    print(f"📁 Data saved securely in '{output_file}'.")
    print("="*60 + "\n")

if __name__ == "__main__":
    if os.name == 'nt':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(process_bulk_links_async())