import asyncio
import json
import os
import sys
import time
import urllib.parse
from curl_cffi.requests import AsyncSession
from selectolax.parser import HTMLParser
from rich import print as rprint
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn

# ==========================================
# 🚀 UNIVERSAL UTILS INTEGRATION
# ==========================================
# Ye automatically 4 folders peeche jaakar utils ko dhoondhega 
# (Script -> sitemap -> fetch_prod_senco -> backend -> root_path)
root_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

if root_path not in sys.path:
    sys.path.append(root_path)

from utils import detect_category, get_formatted_date

# 🚀 TARGET URL
TARGET_URL = "https://sencogoldanddiamonds.com/jewellery/category/everlite-festive-collection"
OUTPUT_FILE = "senco_links_new.json" # Tumhari existing file

async def main():
    rprint("\n[bold magenta]==========================================[/bold magenta]")
    rprint("[bold magenta] 🎯 SENCO SINGLE-URL DEEP DIVE HARVESTER [/bold magenta]")
    rprint("[bold magenta]==========================================[/bold magenta]\n")

    all_final_products = []
    unique_skus = set()

    # -----------------------------------------------------
    # 1. LOAD EXISTING 12K+ DATABASE
    # -----------------------------------------------------
    if os.path.exists(OUTPUT_FILE):
        try:
            with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
                existing_data = json.load(f)
                all_final_products.extend(existing_data)
                for item in existing_data:
                    if item.get("sku"): unique_skus.add(item["sku"])
            rprint(f"[green]📂 Loaded {len(unique_skus)} existing SKUs from '{OUTPUT_FILE}'.[/green]\n")
        except Exception: pass

    initial_count = len(unique_skus)
    categories_to_search = set()
    
    # Base category bhi add kar lete hain just in case
    base_cat = TARGET_URL.split('/')[-1].replace('-', ' ').strip()
    categories_to_search.add(base_cat)

    async with AsyncSession() as session:
        # -----------------------------------------------------
        # 2. FETCH FILTERS FROM TARGET URL
        # -----------------------------------------------------
        rprint(f"[yellow]🔍 PHASE 1: Fetching filters from: {TARGET_URL}[/yellow]")
        try:
            response = await session.get(TARGET_URL, impersonate="chrome120", timeout=15)
            if response.status_code == 200:
                tree = HTMLParser(response.text)
                
                # Tumhare screenshot wala exact CSS logic
                filter_items = tree.css('div[class*="product_list_filter_section"] li')
                for node in filter_items:
                    cat_text = node.text(strip=True)
                    if cat_text and len(cat_text) > 2:
                        clean_text = cat_text.split('(')[0].strip().lower()
                        if clean_text and clean_text not in ["category", "categories"]:
                            categories_to_search.add(clean_text)
                            
                rprint(f"[green]✅ Found {len(categories_to_search)} specific sub-categories on this page.[/green]\n")
            else:
                rprint(f"[red]❌ Failed to fetch URL. Status: {response.status_code}[/red]\n")
        except Exception as e:
            rprint(f"[red]⚠️ Error fetching filters: {e}[/red]\n")

        # -----------------------------------------------------
        # 3. QUERY UNBXD API FOR EACH FILTER
        # -----------------------------------------------------
        rprint("[yellow]🔄 PHASE 2: Searching Unbxd API for these categories...[/yellow]")
        
        with Progress(
            SpinnerColumn("dots", style="cyan"),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(complete_style="green", finished_style="green"),
            TaskProgressColumn()
        ) as progress:
            task = progress.add_task("[cyan]Querying API...", total=len(categories_to_search))
            
            for cat in categories_to_search:
                page = 1
                rows = 100
                encoded_cat = urllib.parse.quote(cat)
                current_time = int(time.time() * 1000)
                uid = f"uid-{current_time}-48347"
                
                while True:
                    # Tumhari nayi waali powerful API query
                    api_url = f"https://search.unbxd.io/2f0815a68672fd25b4b7992b72302e5b/ss-unbxd-aapac-prod-sencogold56671721125516/search?q={encoded_cat}&rows={rows}&page={page}&uid={uid}&variants=true&pagetype=boolean&fields=title,sku,productUrl"
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36',
                        'Origin': 'https://sencogoldanddiamonds.com',
                        'Referer': 'https://sencogoldanddiamonds.com/'
                    }
                    
                    try:
                        res = await session.get(api_url, headers=headers, impersonate="chrome120", timeout=15)
                        if res.status_code != 200: break
                        
                        data = res.json()
                        items = data.get('response', {}).get('products', [])
                        if not items: break
                        
                        for item in items:
                            sku = item.get('sku')
                            # 🛑 STRICT DUPLICATE CHECK
                            if sku and sku not in unique_skus:
                                unique_skus.add(sku)
                                title = item.get('title', '')
                                raw_url = item.get('productUrl', '')
                                full_url = raw_url if raw_url.startswith('http') else f"https://sencogoldanddiamonds.com/{raw_url.lstrip('/')}"
                                
                                all_final_products.append({
                                    "Brand": "Senco",
                                    "product_url": full_url,
                                    "sku": sku,
                                    "title": title,
                                    "category": detect_category(title)
                                })
                        
                        page += 1
                        await asyncio.sleep(0.2) # API ko saans lene do
                    except Exception:
                        break
                
                progress.update(task, advance=1)

    # -----------------------------------------------------
    # 4. FINAL REPORT & SAVE
    # -----------------------------------------------------
    new_items = len(unique_skus) - initial_count
    
    if new_items > 0:
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(all_final_products, f, indent=4)
            
    rprint("\n[bold green]==========================================[/bold green]")
    rprint(f"[bold white on green] 🎉 MISSION ACCOMPLISHED! Saved {new_items} NEW items. [/bold white on green]")
    rprint(f"[cyan] 📦 Total Products now in DB: {len(all_final_products)} [/cyan]")
    rprint("[bold green]==========================================[/bold green]\n")

if __name__ == "__main__":
    if os.name == 'nt':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())