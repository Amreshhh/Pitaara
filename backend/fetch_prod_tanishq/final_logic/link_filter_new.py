import asyncio
import json
import time
import sys
import os
from curl_cffi.requests import AsyncSession
from selectolax.parser import HTMLParser
from datetime import datetime
import re # Isey file ke top par imports me daal dena

# 🚀 MONGODB IMPORTS
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from dotenv import load_dotenv
from pymongo import UpdateOne

# 🚀 MODULE IMPORTS
from link_filter_puregold import extract_basic_details
from link_filter_api import extract_via_api

# 🚀 NAYA: Rich Library Imports
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, TimeElapsedColumn

# ==========================================
# 🚀 UTILS INTEGRATION (Bulletproof Logic)
# ==========================================
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
root_path = os.path.dirname(parent_dir)

if root_path not in sys.path:
    sys.path.append(root_path)

from utils import detect_category, get_formatted_date, detect_tanishq_type
# ==========================================
# 🚀 MONGODB SETUP
# ==========================================
# Pointing specifically to the frontend folder for the .env file based on your tree
env_path = os.path.join(root_path, ".env")
load_dotenv(env_path)

MONGO_URI = os.getenv("MONGO_URI")
if not MONGO_URI:
    print(f"❌ ERROR: MONGO_URI not found! Checking at: {env_path}")
    sys.exit(1)

try:
    client = MongoClient(MONGO_URI)
    db = client['jewelry_database']  # Replace with your actual database name if different
    collection = db['tanishq_products']
    # Quick ping to verify connection
    client.admin.command('ping')
    print("✅ Successfully connected to MongoDB!")
except Exception as e:
    print(f"❌ MongoDB Connection Failed: {e}")
    sys.exit(1)

# --- CONFIGURATION ---
INPUT_FILE = 'tanishq_earrings_urls.json'
OUTPUT_FILE = 'tanishq_final_database.json'  # Keeping local JSON as a backup
CONCURRENCY_LIMIT = 100
# ==========================================
# THE DISPATCHER (MASTER CONTROLLER)
# ==========================================
async def process_product(url, session, semaphore):
    async with semaphore:
        for attempt in range(3):
            try:
                response = await session.get(url, timeout=30)
                tree = HTMLParser(response.text)
                
                # ==========================================
                # CONDITION 1: SUPER CHECK OUT OF STOCK
                # ==========================================
                html_lower = response.text.lower()
                is_out_of_stock = False
                
                if tree.css_first('.pdp-out-of-stock, .out-of-stock, .stock-unavailable'):
                    is_out_of_stock = True
                elif 'schema.org/outofstock' in html_lower or 'schema.org/soldout' in html_lower:
                    is_out_of_stock = True
                elif '"availability":"outofstock"' in html_lower.replace(' ', ''):
                    is_out_of_stock = True
                
                if not is_out_of_stock:
                    cart_btn = tree.css_first('button.add-to-cart, .add-to-cart-btn')
                    if cart_btn and 'out of stock' in cart_btn.text(strip=True).lower():
                        is_out_of_stock = True

                if is_out_of_stock:
                    return None

                # ==========================================
                # 3. EXTRACT SKU ID
                # ==========================================
                pid = None
                sku_node = tree.css_first('.evgProductSKU')
                if sku_node:
                    pid = sku_node.text(strip=True).lower()
                else:
                    for span in tree.css('span'):
                        if 'SKU ID' in span.text():
                            if span.next: pid = span.next.text(strip=True).lower()
                            break

                # ==========================================
                # CONDITION 2: THE SMART FILTER (Check for Diamonds/Stones)
                # ==========================================
                is_stone = False
                html_text_upper = response.text.upper()
                url_lower_check = url.lower()
                
                if 'diamond' in url_lower_check or 'stone' in url_lower_check or 'gemstone' in url_lower_check:
                    is_stone = True
                elif 'DIAMOND DETAILS' in html_text_upper or 'STONE DETAILS' in html_text_upper:
                    is_stone = True
                else:
                    spec_blocks = tree.css('.col-lg-4.col-6.mb-4')
                    for block in spec_blocks:
                        lbl = block.css_first('p')
                        val = block.css_first('h4')
                        if lbl and val and 'jewellery type' in lbl.text(strip=True).lower():
                            v_text = val.text(strip=True).lower()
                            if 'stone' in v_text or 'gemstone' in v_text:
                                is_stone = True
                                break

                # ==========================================
                # ROUTE TO THE CORRECT ENGINE (With Detailed Type)
                # ==========================================
                needs_api, detailed_type = detect_tanishq_type(url, response.text, tree)

                if needs_api and pid:
                    # Pass detailed_type inside the function
                    result = await extract_via_api(url, tree, pid, session, detailed_type)
                else:
                    # Pass detailed_type inside the function
                    result = extract_basic_details(url, tree, pid, detailed_type)

                # 🚀 INJECT CATEGORY & DATE FROM UTILS
                if result:
                    result["category"] = detect_category(url) 
                    result["extraction_date"] = get_formatted_date() 
                    return result
                
                return None

            except Exception as e:
                if attempt < 2:
                    await asyncio.sleep(2)
                else:
                    return None

async def main():
    print("📂 Loading URLs...")
    
    if not os.path.exists(INPUT_FILE):
        print(f"❌ Input file {INPUT_FILE} not found!")
        return
        
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        urls = json.load(f)
    final_master_data = []

  

    # 🚀 LIVE MONGO DB AUTO-RESUME LOGIC (The Regex Sniper)
    scraped_urls = set()
    scraped_skus = set()

    def super_clean_url(u):
        """URL se saara kachra (?, /, .html) nikal deta hai exact URL match ke liye"""
        u = u.split('?')[0].rstrip('/')
        if u.endswith('.html'):
            u = u[:-5]
        return u.lower()

    def extract_sku_smartly(url):
        """ .html ke theek pehle aane wala SKU nikalta hai (Number se shuru hone wala) """
        base_url = url.split('?')[0].rstrip('/')
        
        # Regex Magic: .html (ya end of string) se theek pehle wala number se shuru hone wala block
        match = re.search(r'(\d[a-zA-Z0-9]*)(?:\.html)?$', base_url)
        
        if match:
            return match.group(1).lower() # Output: 513919sjbaba00
            
        # Agar regex fail hua (kabhi-kabhi alag URL format aa jata hai), toh fallback
        return super_clean_url(url).split('-')[-1]

    print("🔄 Fetching existing records from MongoDB to compare...")
    try:
        existing_docs = collection.find({}, {"product_url": 1, "sku": 1})
        for doc in existing_docs:
            if doc.get("product_url"):
                scraped_urls.add(super_clean_url(doc["product_url"]))
            
            if doc.get("sku"):
                scraped_skus.add(doc["sku"].lower())
                
        print(f"✅ Found {len(scraped_urls)} URLs and {len(scraped_skus)} SKUs inside DB.")
    except Exception as e:
        print(f"⚠️ Could not fetch from MongoDB: {e}")

    # 🚀 NEW: THE ULTIMATE ZERO-REQUEST FILTER
    pending_urls = []
    
    print("🕵️‍♂️ Filtering out duplicates...")
    for url in urls:
        clean_input_url = super_clean_url(url)
        possible_sku = extract_sku_smartly(url) # Naya smart checker call hua
        
        # 🛑 DOUBLE SHIELD CHECK 
        if clean_input_url in scraped_urls:
            continue # Shield 1: Exact URL match
            
        if possible_sku in scraped_skus:
            continue # Shield 2: SKU match ho gaya
            
        pending_urls.append(url)

    total_items = len(pending_urls)

    print(f"🎯 Found {total_items} pending products to process.\n")
    start = time.time()
    
    semaphore = asyncio.Semaphore(CONCURRENCY_LIMIT)
    
    async with AsyncSession(impersonate="chrome120") as session:
        await session.get("https://www.tanishq.co.in") # Cookie grab
        
        tasks = [process_product(url, session, semaphore) for url in pending_urls]
        completed_tasks = 0 
            
        with Progress(
            SpinnerColumn("moon", style="bold green"), 
            TextColumn("[bold cyan]{task.description}"), 
            BarColumn(
                bar_width=50, 
                style="grey37", 
                complete_style="bold chartreuse1" 
            ),
            TaskProgressColumn(style="bold magenta"), 
            TextColumn("[bold yellow]{task.completed}/{task.total}"),          
            TimeElapsedColumn(),
        ) as progress:
            
            task_id = progress.add_task("[cyan]🚀 Fetching Tanishq Data...", total=total_items)

            try:
                for future in asyncio.as_completed(tasks):
                    result = await future
                    completed_tasks += 1
                    
                    if result:
                        final_master_data.append(result)
                        
                        # 💾 SEEDHA MONGODB MEIN LIVE PUSH
                        # Upsert ensures ki agar galti se duplicate fetch hua to update ho jayega
                        try:
                            collection.update_one(
                                {"product_url": result["product_url"]},
                                {"$set": result},
                                upsert=True
                            )
                        except PyMongoError as db_err:
                            progress.console.print(f"[red]⚠️ MongoDB Save Error: {db_err}[/red]")
                    
                    progress.update(task_id, advance=1)
                    
                    # 💾 JSON BACKUP (Har 20 items ke baad local file update)
                    if completed_tasks % 20 == 0 and final_master_data:
                        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
                            json.dump(final_master_data, f, indent=4, ensure_ascii=False)
                            
            except KeyboardInterrupt:
                progress.console.print("\n[red]🛑 Stopped by User. Progress database mein already safe hai![/red]")
            
            finally:
                # 💾 FINAL JSON SAVE
                if final_master_data:
                    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
                        json.dump(final_master_data, f, indent=4, ensure_ascii=False)
        
    print(f"\n🎉 BOOM! Finished filtering and extraction in {round(time.time() - start, 2)} seconds.")
    print(f"💾 Data seamlessly synced to MongoDB collection: '{collection.name}'")

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())