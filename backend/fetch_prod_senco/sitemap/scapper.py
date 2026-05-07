import json
import asyncio
import os
import sys
import time
from curl_cffi.requests import AsyncSession
from rich import print as rprint
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, TimeElapsedColumn

# 🚀 NEW IMPORTS FOR MONGODB & ENV
from pymongo import MongoClient, UpdateOne
from dotenv import load_dotenv

# 🚀 LOCAL IMPORTS
from extractor import extract_senco_breakup_python

root_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if root_path not in sys.path:
    sys.path.append(root_path)

# Fallback for utils
try:
    from utils import get_formatted_date, check_if_diamond 
except ImportError:
    def get_formatted_date(): return time.strftime("%Y-%m-%d %H:%M:%S")
    def check_if_diamond(t, b): return "Gold (Scraped)"

# ==========================================
# 🚀 MONGODB SETUP
# ==========================================
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")

if not MONGO_URI:
    rprint("[bold red]❌ Error: MONGO_URI not found in .env file![/bold red]")
    sys.exit(1)

# Connect to MongoDB based on your screenshot structure
client = MongoClient(MONGO_URI)
db = client["jewelry_database"]
senco_collection = db["senco_products"]

# ==========================================
# 🚀 ASYNC FETCHER
# ==========================================
async def fetch_senco_product(session, item, semaphore):
    product_url = item.get("product_url")
    sku = item.get("sku", "Unknown")
    
    if not product_url: return None

    async with semaphore:
        try:
            response = await session.get(product_url, impersonate="chrome120", timeout=25)
            
            if response.status_code == 404:
                return None 
                
            if response.status_code != 200:
                return None

            breakup = extract_senco_breakup_python(response.text, product_url, item.get("title", ""))
            final_type = check_if_diamond(item.get("title", ""), breakup)

            return {
                "Brand": "Senco",
                "product_url": product_url,
                "sku": sku,
                # "title": item.get("title", ""),
                "type": final_type, 
                "purity": breakup.get("purity", "Unknown"),
                "net_weight": breakup.get("net_weight", 0.0),
                # "gross_weight": breakup.get("gross_weight", 0.0),
                "making_charges_percentage": breakup.get("making_charge_percentage", "N/A"),
                # "stone_charges": breakup.get("stone_charges", 0.0),
                # "platinum_weight": breakup.get("platinum_weight", 0.0),
                # "platinum_purity": breakup.get("platinum_purity", "Unknown"),
                "extraction_date": get_formatted_date(),
                "category": item.get("category", "Other"),
            }

        except Exception as e:
            return None

# ==========================================
# 🚀 THE MASTER 12K LOOP (WITH MONGODB PUSH)
# ==========================================
async def run_senco_massive_scraper():
    input_file = "senco_links_new.json" 
    output_file = "senco_final_detailed_data.json"
    error_file = "senco_missing_prices.json"
    
    rprint(f"\n[bold blue]📂 Loading 12K+ URLs from {input_file}...[/bold blue]")
    try:
        with open(input_file, "r", encoding="utf-8") as f:
            links_data = json.load(f)
    except FileNotFoundError:
        rprint(f"[bold red]❌ Error: '{input_file}' file nahi mili![/bold red]")
        return

    final_master_data = []
    missing_data_items = []
    scraped_urls = set()
    
    # 🛑 RESUME LOGIC (Checking both JSON and MongoDB)
    try:
        # Check kitne URL already MongoDB me hain taaki dobara scrape na kare
        existing_docs = senco_collection.find({}, {"product_url": 1})
        for doc in existing_docs:
            scraped_urls.add(doc.get("product_url"))
        rprint(f"[bold yellow]🔄 Found {len(scraped_urls)} items already in MongoDB. Resuming...[/bold yellow]")
    except Exception as e:
        rprint(f"[bold red]⚠️ Could not fetch from MongoDB for resume logic: {e}[/bold red]")

    pending_links = [link for link in links_data if link.get("product_url") not in scraped_urls]
    total_items = len(pending_links)

    if total_items == 0:
        rprint("[bold green]🎉 All Senco products have been fully scraped and pushed to MongoDB![/bold green]")
        return

    rprint(f"[bold cyan]🎯 Starting Deep Extraction for {total_items} pending items...[/bold cyan]\n")
    
    CONCURRENCY = 30  
    semaphore = asyncio.Semaphore(CONCURRENCY)
    mongo_batch_ops = [] # 🚀 DB batch ops list
    
    async with AsyncSession() as session:
        tasks = [fetch_senco_product(session, i, semaphore) for i in pending_links]
        
        with Progress(
            SpinnerColumn("bouncingBar", style="yellow"),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(complete_style="cyan", finished_style="green"),
            TaskProgressColumn(),
            TimeElapsedColumn(),
        ) as progress:
            
            task_id = progress.add_task("[cyan]🚀 Scraping & Pushing to DB...", total=total_items)

            try:
                for future in asyncio.as_completed(tasks):
                    result = await future
                    if result:
                        # Error / Zero value filter
                        if result.get("making_charge_percentage") == "N/A":
                            missing_data_items.append(result)
                        else:
                            final_master_data.append(result)
                            
                            # 🚀 MONGODB UPSERT PREPARATION
                            # Hum product_url ko primary key maan kar Upsert laga rahe hain
                            op = UpdateOne(
                                {"product_url": result["product_url"]}, 
                                {"$set": result}, 
                                upsert=True
                            )
                            mongo_batch_ops.append(op)
                    
                    progress.update(task_id, advance=1)
                    
                    # 💾 AUTO-SAVE & DB PUSH (Every 50 items)
                    if progress.tasks[0].completed % 50 == 0:
                        
                        # 1. MongoDB Bulk Write
                        if mongo_batch_ops:
                            try:
                                senco_collection.bulk_write(mongo_batch_ops, ordered=False)
                                mongo_batch_ops.clear() # Batch clear karo agle 50 ke liye
                            except Exception as e:
                                pass # Silent fail on write error to keep loop going
                        
                        # 2. Local JSON Backup Write
                        with open(output_file, "w", encoding="utf-8") as f:
                            json.dump(final_master_data, f, indent=4)
                        if missing_data_items:
                            with open(error_file, "w", encoding="utf-8") as f:
                                json.dump(missing_data_items, f, indent=4)
                                
            except KeyboardInterrupt:
                rprint("\n[bold red]🛑 Stopped by User. Saving progress before exit...[/bold red]")
            finally:
                # Final cleanup save & push
                if mongo_batch_ops:
                    try:
                        senco_collection.bulk_write(mongo_batch_ops, ordered=False)
                    except Exception: pass
                    
                with open(output_file, "w", encoding="utf-8") as f:
                    json.dump(final_master_data, f, indent=4)

    rprint("\n[bold green]" + "="*60 + "[/bold green]")
    rprint(f"[bold white on green] 🎉 PHASE 3 COMPLETE! Pushed to DB & Saved {len(final_master_data)} items. [/bold white on green]")
    rprint("[bold green]" + "="*60 + "[/bold green]\n")

if __name__ == "__main__":
    if os.name == 'nt':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(run_senco_massive_scraper())