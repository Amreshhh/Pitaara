import json
import asyncio
import os
import re
import sys
import requests as sync_requests
from curl_cffi.requests import AsyncSession

# 🚀 NAYA: Rich Library ke imports (tqdm hata diya)
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, TimeElapsedColumn

# ==========================================
# 🚀 UTILS INTEGRATION
# ==========================================
current_dir = os.path.abspath(__file__)
logic_folder = os.path.dirname(current_dir)
kalyan_folder = os.path.dirname(logic_folder)
root_path = os.path.dirname(kalyan_folder) 

sys.path.append(root_path)

from utils import detect_category, get_formatted_date, check_if_diamond 

LINKS_FILE = 'candere_all_links.json'
MASTER_FILE = 'candere_final_data1.json'

# ==========================================
# 🚀 PHASE 1: KLEVU API FETCH 
# ==========================================
def get_or_fetch_links():
    api_url = "https://eucs27v2.ksearchnet.com/cs/v2/search"
    limit = 100
    all_products = []
    offset = 0

    if os.path.exists(LINKS_FILE):
        print(f"📂 Found existing cache ({LINKS_FILE}). Loading...")
        with open(LINKS_FILE, 'r', encoding='utf-8') as f:
            all_products = json.load(f)
        offset = len(all_products)

    if offset > 0:
        print(f"🚀 Resuming Klevu extraction from offset {offset}...")
    else:
        print("🌐 No cache found. Starting fresh Klevu extraction...")

    has_more = True
    while has_more:
        payload = {
            "recordQueries": [{
                "id": "productSearch",
                "typeOfRequest": "SEARCH",
                "settings": {
                    "query": { "term": "Ring" }, 
                    "offset": offset,
                    "limit": limit,
                    "typeOfRecords": ["KLEVU_PRODUCT"]
                }
            }],
            "context": { "apiKeys": ["klevu-163066607292713309"] }
        }

        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

        try:
            response = sync_requests.post(api_url, json=payload, headers=headers)
            if response.status_code != 200:
                print(f"HTTP Error: {response.status_code}")
                break
                
            data = response.json()
            records = data.get("queryResults", [{}])[0].get("records", [])

            if not records:
                print("✅ Reached the end of the Klevu catalog.")
                break

            for item in records:
                name = item.get("name", "")
                url = item.get("url", "")
                sku = item.get("id", "")
                
                category_str = detect_category(name)

                all_products.append({
                    "Brand": "Candere",
                    "product_url": url,
                    "sku": sku,
                    "title": name, 
                    "category": category_str  
                })

            print(f"📦 Fetched from Klevu! Total so far: {len(all_products)}")
            offset += limit

            with open(LINKS_FILE, 'w', encoding='utf-8') as f:
                json.dump(all_products, f, indent=4)

        except Exception as e:
            print(f"⚠️ Error fetching data: {e}")
            break

    return all_products

# ==========================================
# 🚀 EXTRACTOR LOGIC
# ==========================================
def extract_candere_breakup(html_content):
    default_breakup = {
        "purity": "Unknown",
        "gross_weight": 0.0,
        "making_charges_percentage": "0 %",
        "stone_charges": 0.0 
    }

    try:
        split1 = html_content.split('var defaultProJson =')
        if len(split1) < 2: return default_breakup
        
        raw_json_str = split1[1].split('};')[0].strip() + '}'
        json_data = json.loads(raw_json_str)

        purity_text = 'Unknown'
        metal_arr = json_data.get("metal", [])
        if metal_arr:
            raw_purity = metal_arr[0].get("purity", "")
            match = re.search(r'(\d+)', raw_purity)
            purity_text = f"{match.group(1)}K" if match else raw_purity

        total_stone_value = float(json_data.get("discount_stone_price") or json_data.get("stone_price") or 0) + \
                            float(json_data.get("discount_gemstone_price") or json_data.get("gemstone_price") or 0) + \
                            float(json_data.get("discount_zirconia_price") or json_data.get("zirconia_price") or 0)

        gold_value = float(json_data.get("metal_price") or 0)
        making_charges = float(json_data.get("discount_making_charge") or json_data.get("making_charge") or 0)

        mc_percentage_str = "N/A"
        if gold_value > 0:
            mc_percentage = (making_charges / gold_value) * 100
            mc_percentage_str = f"{round(mc_percentage, 2)} %"

        return {
            "purity": purity_text,
            "gross_weight": float(json_data.get("total_metal_weight") or 0),
            "making_charges_percentage": mc_percentage_str,
            "stone_charges": total_stone_value 
        }

    except Exception as e:
        return default_breakup

# ==========================================
# 🚀 ASYNC FETCHER (PHASE 2)
# ==========================================
async def fetch_product_details(session, product, semaphore):
    raw_url = product.get("product_url", "")
    if not raw_url: return None

    target_url = raw_url if raw_url.startswith('http') else f"https://www.candere.com{'' if raw_url.startswith('/') else '/'}{raw_url}"

    async with semaphore:
        try:
            response = await session.get(target_url, impersonate="chrome120", timeout=20)
            if response.status_code != 200: return None

            detailed_breakup = extract_candere_breakup(response.text)

            product_title = product.get("title", "")
            product_type = check_if_diamond(product_title, detailed_breakup)
            extracted_date = get_formatted_date()

            return {
                "Brand": "Candere",
                "product_url": target_url,
                "sku": product.get("sku"),
                "type": product_type,
                "purity": detailed_breakup["purity"],
                "net_weight": detailed_breakup["gross_weight"],
                "making_charges_percentage": detailed_breakup["making_charge_percentage"],
                "category": product.get("category", "Ring"),
                "extraction_date": extracted_date 
            }
        except Exception:
            return None

# ==========================================
# 🚀 MASTER PIPELINE
# ==========================================
async def run_master_pipeline():
    all_products = get_or_fetch_links()
    
    if not all_products:
        return

    master_data = []
    scraped_skus = set()

    if os.path.exists(MASTER_FILE):
        try:
            with open(MASTER_FILE, "r", encoding="utf-8") as f:
                content = f.read()
                if content.strip():
                    master_data = json.loads(content)
                    scraped_skus = {item.get("sku") for item in master_data if item.get("sku")}
            print(f"🔄 Loaded {len(scraped_skus)} previously scraped products.")
        except json.JSONDecodeError: pass

    pending_products = [p for p in all_products if p.get("sku") not in scraped_skus]

    if not pending_products:
        print("🎉 All products are already scraped! Nothing to do.")
        return
        
    print(f"\n🛠️ STARTING PHASE 2: {len(pending_products)} items remaining to scrape...\n")

    CONCURRENCY = 50 
    semaphore = asyncio.Semaphore(CONCURRENCY)
    
    headers = {
        'Accept': 'text/html',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }

    async with AsyncSession(headers=headers) as session:
        tasks = [fetch_product_details(session, p, semaphore) for p in pending_products]
        
        # 🚀 TQDM HATA DIYA - AAGAYA RICH PROGRESS BAR MONKEY KE SATH 🐒
        with Progress(
            SpinnerColumn("monkey", style="bold yellow"),  # 🐒 Masti wala monkey animation!
            TextColumn("[progress.description]{task.description}"),
            BarColumn(complete_style="cyan", finished_style="bold green"), # 🎨 Custom UI colors
            TaskProgressColumn(),
            TimeElapsedColumn(),
        ) as progress:
            
            # Task create kiya aur total length batayi
            task_id = progress.add_task("[magenta]🚀 Fetching Candere Data...", total=len(tasks))

            for future in asyncio.as_completed(tasks):
                result = await future
                if result:
                    master_data.append(result)
                
                # Bar ko 1 step aage badhao
                progress.update(task_id, advance=1)
                
                # Check karo kitne tasks complete ho gaye
                current_completed = progress.tasks[task_id].completed
                
                # Agar 20 items complete ho gaye hain toh save maar do
                if current_completed % 20 == 0:
                    with open(MASTER_FILE, "w", encoding="utf-8") as f:
                        json.dump(master_data, f, indent=4)

    # Jab loop khatam ho jaye toh final save maar do
    with open(MASTER_FILE, "w", encoding="utf-8") as f:
        json.dump(master_data, f, indent=4)

    print("\n🎉 CANDERE PIPELINE COMPLETE!")
    if master_data: print(json.dumps(master_data[-1], indent=4))

if __name__ == "__main__":
    if os.name == 'nt':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(run_master_pipeline())