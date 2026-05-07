import json
import asyncio
import os
import sys
from curl_cffi.requests import AsyncSession
from dotenv import load_dotenv

# 🚀 Rich Library Imports
from rich import print as rprint
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, TimeElapsedColumn

# 🚀 MongoDB Async Driver
from motor.motor_asyncio import AsyncIOMotorClient

# ==========================================
# 🚀 UNIVERSAL UTILS INTEGRATION
# ==========================================
root_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

if root_path not in sys.path:
    sys.path.append(root_path)

# Utils se imported functions
try:
    from utils import detect_category, get_formatted_date, check_if_diamond 
except ImportError:
    def detect_category(name): return "Gold Jewellery"
    def get_formatted_date(): return "2026-04-29"
    def check_if_diamond(url, breakup): return "Diamond" if breakup.get('stone_charges', 0) > 0 else "Gold"

# =========================================================
# 🛠️ ENV & DATABASE SETUP
# =========================================================
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")

if not MONGO_URI:
    rprint("[bold red]❌ Error: MONGO_URI not found in .env file![/bold red]")
    sys.exit(1)

# Initialize MongoDB Client
mongo_client = AsyncIOMotorClient(MONGO_URI)
db = mongo_client["jewelry_database"]
collection = db["malabar_products"]

# =========================================================
# 🛠️ MALABAR SPECIFIC HELPER FUNCTIONS 
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
            product_name = item.get("name", "")
            breakup = item.get("price_breakup")

            if not breakup and item.get("variants"):
                variant_product = item["variants"][0].get("product", {})
                breakup = variant_product.get("price_breakup")
                
            if not breakup: return None
            
            # --- Purity Logic ---
            raw_purity = breakup.get("purity", "")
            clean_purity = parse_malabar_purity(raw_purity)
            
            # --- Core Values ---
            gold_value = parse_malabar_number(breakup.get("metal_charges"))
            making_charge = parse_malabar_number(breakup.get("making_charges"))
            total_stone_charges = parse_malabar_number(breakup.get("diamond_charges")) + parse_malabar_number(breakup.get("stone_charges"))
            
            # --- Making Charge Percentage Logic ---
            mc_percent = 0
            if gold_value > 0:
                mc_percent = round((making_charge / gold_value) * 100, 2)

            # --- Type Logic via utils.py ---
            mock_breakup = {
                'stone_charges': total_stone_charges,
                'purity': clean_purity 
            }
            final_type = check_if_diamond(product_name, mock_breakup)

            # --- Category Logic via utils.py ---
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
                "extraction_date": get_formatted_date()
            }
            
            return final_output

        except Exception as e:
            return None

# =========================================================
# 🚀 THE MASTER CONTINUOUS PROCESSING LOOP
# =========================================================
async def process_bulk_links_async():
    input_file = "malabar_all_19k_links.json"
    
    rprint(f"\n[bold blue]📂 Loading links from {input_file}...[/bold blue]")
    try:
        with open(input_file, "r", encoding="utf-8") as f:
            links_data = json.load(f)
    except FileNotFoundError:
        rprint(f"[bold red]❌ Error: File '{input_file}' not found.[/bold red]")
        return

    # 🚀 MONGODB AUTO-RESUME LOGIC
    rprint("[bold cyan]🔍 Checking MongoDB for already scraped items...[/bold cyan]")
    try:
        # Fetch only SKUs to save memory
        existing_docs_cursor = collection.find({}, {"sku": 1})
        existing_docs = await existing_docs_cursor.to_list(length=None)
        scraped_skus = {doc["sku"] for doc in existing_docs if "sku" in doc}
        rprint(f"[bold yellow]🔄 Found {len(scraped_skus)} items already in 'malabar_products'. Skipping those...[/bold yellow]")
    except Exception as e:
        rprint(f"[bold red]❌ Failed to connect to MongoDB: {e}[/bold red]")
        return

    pending_links = [link for link in links_data if link.get("sku") not in scraped_skus]
    total_items = len(pending_links)

    if total_items == 0:
        rprint("[bold green]🎉 Saara data database mein pehle se majood hai! You are 100% done.[/bold green]")
        return

    rprint(f"[bold cyan]🎯 Found {total_items} pending products to process.[/bold cyan]\n")
    
    CONCURRENCY = 50  
    semaphore = asyncio.Semaphore(CONCURRENCY)
    
    headers = {
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Referer": "https://www.malabargoldanddiamonds.com/",
        "Origin": "https://www.malabargoldanddiamonds.com",
    }

    inserted_count = 0

    async with AsyncSession(headers=headers) as session:
        tasks = []
        for item in pending_links:
            sku = item.get("sku")
            url = item.get("product_url")
            if sku:
                tasks.append(fetch_product_breakup_async(session, sku, url, semaphore))
        
        with Progress(
            SpinnerColumn("bouncingBar", style="yellow"),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(complete_style="magenta", finished_style="green"),
            TaskProgressColumn(),
            TimeElapsedColumn(),
        ) as progress:
            
            task_id = progress.add_task("[cyan]🚀 Extracting & Pushing to MongoDB...", total=total_items)

            try:
                for future in asyncio.as_completed(tasks):
                    result = await future
                    if result:
                        # 🚀 REAL-TIME PUSH TO MONGODB (Upsert prevents duplicates)
                        await collection.update_one(
                            {"sku": result["sku"]},
                            {"$set": result},
                            upsert=True
                        )
                        inserted_count += 1
                    
                    progress.update(task_id, advance=1)
                        
            except KeyboardInterrupt:
                rprint("\n[bold red]🛑 Stopped by User. Progress is safe in MongoDB.[/bold red]")

    rprint("\n[bold green]" + "="*60 + "[/bold green]")
    rprint(f"[bold white on green] 🎉 ASYNC PIPELINE COMPLETE! [/bold white on green]")
    rprint(f"[bold green]📁 Successfully pushed {inserted_count} new products to MongoDB Collection: 'malabar_products'.[/bold green]")
    rprint("[bold green]" + "="*60 + "[/bold green]\n")

if __name__ == "__main__":
    if os.name == 'nt':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(process_bulk_links_async())