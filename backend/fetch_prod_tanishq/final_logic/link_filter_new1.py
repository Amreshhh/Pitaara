import asyncio
import json
import time
import sys
import os
from curl_cffi.requests import AsyncSession
from selectolax.parser import HTMLParser
from datetime import datetime

# 🚀 MODULE IMPORTS
from link_filter_puregold import extract_basic_details
from link_filter_api import extract_via_api

# 🚀 NAYA: Rich Library Imports
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, TimeElapsedColumn, MofNCompleteColumn

# ==========================================
# 🚀 UTILS INTEGRATION (Bulletproof Logic)
# ==========================================
# Script jis folder mein hai wahan se 2 level upar (root) jaana hai
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
root_path = os.path.dirname(parent_dir)

# Agar path pehle se add nahi hai toh hi add karo (taaki duplicate na ho)
if root_path not in sys.path:
    sys.path.append(root_path)

from utils import detect_category, get_formatted_date, check_if_diamond 

# --- CONFIGURATION ---
INPUT_FILE = 'tanishq_full_database_urls.json'
OUTPUT_FILE = 'tanishq_final_database.json'
CONCURRENCY_LIMIT = 5

# ==========================================
# THE DISPATCHER (MASTER CONTROLLER)
# ==========================================
async def process_product(url, session, semaphore):
    async with semaphore:
        for attempt in range(3):
            try:
                # 1. Fetch the main page
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
                # ROUTE TO THE CORRECT ENGINE
                # ==========================================
                if is_stone and pid:
                    result = await extract_via_api(url, tree, pid, session)
                else:
                    result = extract_basic_details(url, tree, pid)

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

    # Auto-Resume Logic
    final_master_data = []
    scraped_urls = set()
    
    if os.path.exists(OUTPUT_FILE):
        try:
            with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
                content = f.read()
                if content.strip():
                    final_master_data = json.loads(content)
                    scraped_urls = {item.get("product_url") for item in final_master_data if item.get("product_url")}
            print(f"🔄 Found {len(scraped_urls)} already scraped items. Resuming where left off...")
        except json.JSONDecodeError:
            print(f"⚠️ Warning: Output file corrupt hai, fresh start kar rahe hain.")

    pending_urls = [url for url in urls if url not in scraped_urls]
    total_items = len(pending_urls)

    if total_items == 0:
        print("🎉 Saara data pehle hi fetch ho chuka hai! You are 100% done.")
        return

    print(f"🎯 Found {total_items} pending products to process.\n")
    start = time.time()
    
    semaphore = asyncio.Semaphore(CONCURRENCY_LIMIT)
    
    async with AsyncSession(impersonate="chrome120") as session:
        await session.get("https://www.tanishq.co.in") # Cookie grab
        
        tasks = [process_product(url, session, semaphore) for url in pending_urls]
        completed_tasks = 0 # Naya counter save logic ke liye
        
        # 🚀 THE RICH PROGRESS BAR UI
        # with Progress(
        #     SpinnerColumn("bouncingBar", style="yellow"), # Tera Animated GIF
        #     TextColumn("[progress.description]{task.description}"),
        #     BarColumn(complete_style="magenta", finished_style="green"), # Custom Colors
        #     TaskProgressColumn(),
        #     TimeElapsedColumn(),
        # ) as progress:
            
        with Progress(
                    SpinnerColumn("moon", style="bold green"), # Moon ghoomta hua dikhega
                    TextColumn("[bold cyan]{task.description}"), # Glowing Blue Text
                    BarColumn(
                        bar_width=50, # Bar ki motai badha di
                        style="grey37", # Empty bar ka color
                        complete_style="bold chartreuse1" # 🟢 Neon Green complete hone par
                    ),
                    TaskProgressColumn(style="bold magenta"), # 3% likha hua magenta aayega
                    TextColumn("[bold yellow]{task.completed}/{task.total}"),          
                                        TimeElapsedColumn(),
                    ) as progress:
            
            # Progress bar ka task add karo
            task_id = progress.add_task("[cyan]🚀 Fetching Tanishq Data...", total=total_items)

            try:
                for future in asyncio.as_completed(tasks):
                    result = await future
                    completed_tasks += 1
                    
                    if result:
                        final_master_data.append(result)
                    
                    # UI ko update karo
                    progress.update(task_id, advance=1)
                    
                    # 💾 LIVE DATA STORING (Using custom counter)
                    if completed_tasks % 20 == 0:
                        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
                            json.dump(final_master_data, f, indent=4, ensure_ascii=False)
                            
            except KeyboardInterrupt:
                progress.console.print("\n[red]🛑 Stopped by User. Progress save kar rahe hain...[/red]")
            
            finally:
                # 💾 Final Save
                with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
                    json.dump(final_master_data, f, indent=4, ensure_ascii=False)
        
    print(f"\n🎉 BOOM! Finished filtering and extraction in {round(time.time() - start, 2)} seconds.")
    print(f"💾 Total Saved: {len(final_master_data)} items in '{OUTPUT_FILE}'")

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())