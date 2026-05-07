import os
import json
import asyncio
import re
from curl_cffi.requests import AsyncSession
from rich import print as rprint
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, TimeElapsedColumn

# =========================================================
# 🛠️ GLOBAL SETUP & HELPERS
# =========================================================
OUTPUT_FILE = "malabar_all_19k_links.json"

# Ye Lock file corruption roke ga jab multiple tasks ek sath save karne aayenge
file_write_lock = asyncio.Lock()

def format_url_name(name):
    clean = re.sub(r'[^a-zA-Z0-9\s-]', '', name).strip().lower()
    return re.sub(r'\s+', '-', clean)

# 💾 REAL-TIME SAVE FUNCTION (Extract & Push)
async def save_state_to_file(data_list):
    async with file_write_lock:
        # On-the-fly deduplication taaki file hamesha clean rahe
        unique_links = {item['sku']: item for item in data_list}.values()
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(list(unique_links), f, indent=4)

# =========================================================
# 🛠️ STAGE 1: FETCH ALL CATEGORIES
# =========================================================
async def fetch_all_categories(session):
    api_url = 'https://www.malabargoldanddiamonds.com/graphql-magento'
    
    graphql_query = """
    query getCategories($search: String) {
      products(search: $search) {
        aggregations {
          attribute_code
          options { label value count }
        }
      }
    }
    """
    params = {
        "query": graphql_query,
        "variables": json.dumps({"search": ""}) 
    }

    try:
        rprint("[cyan]🔍 Fetching all Category UIDs from Malabar server...[/cyan]")
        response = await session.get(api_url, params=params, impersonate="chrome120", timeout=20)
        data = response.json()
        
        aggregations = data.get("data", {}).get("products", {}).get("aggregations", [])
        categories = []
        
        for agg in aggregations:
            if agg.get("attribute_code") == "category_uid":
                options = agg.get("options", [])
                for opt in options:
                    cat_id = opt.get("value")
                    cat_name = opt.get("label")
                    count = opt.get("count", 0)
                    if cat_id and count > 0:
                        categories.append({"id": cat_id, "name": cat_name, "count": count})
                break
                
        rprint(f"[bold green]✅ Found {len(categories)} different categories to scrape![/bold green]")
        return categories
    except Exception as e:
        rprint(f"[bold red]❌ Failed to fetch categories: {e}[/bold red]")
        return []

# =========================================================
# 🛠️ STAGE 2: FETCH LINKS FOR A SPECIFIC CATEGORY PAGE
# =========================================================
async def fetch_page_links(session, category_uid, current_page, page_size, semaphore):
    api_url = 'https://www.malabargoldanddiamonds.com/graphql-magento'
    
    graphql_query = """
    query products($filter: ProductAttributeFilterInput, $pageSize: Int, $currentPage: Int) {
      products(filter: $filter, pageSize: $pageSize, currentPage: $currentPage) {
        items {
          name
          sku
          price_breakup { barcode }
        }
        page_info { total_pages }
      }
    }
    """
    
    variables_dict = {
        "pageSize": page_size,
        "currentPage": current_page,
        "filter": { "category_uid": { "in": [category_uid] } }
    }

    params = { "query": graphql_query, "variables": json.dumps(variables_dict) }

    async with semaphore:
        try:
            response = await session.get(api_url, params=params, impersonate="chrome120", timeout=25)
            if response.status_code != 200: return [], 0

            data = response.json()
            products_data = data.get("data", {}).get("products", {})
            items = products_data.get("items", [])
            total_pages = products_data.get("page_info", {}).get("total_pages", 0)
            
            page_links = []
            for item in items:
                sku = item.get("sku", "")
                name = item.get("name", "malabar-product")
                
                barcode = ""
                breakup = item.get("price_breakup")
                if breakup and isinstance(breakup, list) and len(breakup) > 0:
                    barcode = breakup[0].get("barcode", "")
                elif isinstance(breakup, dict):
                     barcode = breakup.get("barcode", "")

                formatted_name = format_url_name(name)
                product_url = f"https://www.malabargoldanddiamonds.com/in/pan-india/en/product/{formatted_name}.html?sku={sku}&barcode={barcode}"

                page_links.append({"sku": sku, "name": name, "product_url": product_url})
                
            return page_links, total_pages
        except Exception:
            return [], 0

# =========================================================
# 🚀 MASTER RUNNER: DYNAMIC PAGINATION WITH REAL-TIME PUSH
# =========================================================
async def process_category(session, category, page_size, semaphore, all_links_list, progress, main_task):
    cat_id = category["id"]
    
    # 1. Fetch Page 1
    links, total_pages = await fetch_page_links(session, cat_id, 1, page_size, semaphore)
    all_links_list.extend(links)
    await save_state_to_file(all_links_list) # 🚀 PUSH TO FILE INSTANTLY
    progress.update(main_task, advance=1)
    
    if total_pages > 1:
        # 2. Setup tasks for remaining pages
        tasks = []
        for page_num in range(2, total_pages + 1):
            tasks.append(fetch_page_links(session, cat_id, page_num, page_size, semaphore))
        
        # 3. As pages finish concurrently, append and push to file
        for future in asyncio.as_completed(tasks):
            res_links, _ = await future
            all_links_list.extend(res_links)
            await save_state_to_file(all_links_list) # 🚀 PUSH TO FILE INSTANTLY
            progress.update(main_task, advance=1)

async def main_async_scraper():
    page_size = 100 
    all_links = []
    
    # Check if file exists to resume gracefully (optional but safe)
    if os.path.exists(OUTPUT_FILE):
        try:
            with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
                all_links = json.load(f)
            rprint(f"[bold yellow]🔄 Resuming with {len(all_links)} existing links...[/bold yellow]")
        except: pass

    semaphore = asyncio.Semaphore(15)
    
    headers = {
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Referer": "https://www.malabargoldanddiamonds.com/",
    }

    async with AsyncSession(headers=headers) as session:
        categories = await fetch_all_categories(session)
        if not categories:
            rprint("[bold red]No categories found. Exiting.[/bold red]")
            return

        estimated_total_calls = sum([(cat["count"] // page_size) + 1 for cat in categories])

        rprint(f"\n[bold cyan]🚀 Starting deep extraction across {len(categories)} categories. Pushing to file in real-time...[/bold cyan]")
        
        tasks = []
        with Progress(
            SpinnerColumn("bouncingBar", style="yellow"),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(complete_style="magenta", finished_style="green"),
            TaskProgressColumn(),
            TimeElapsedColumn(),
        ) as progress:
            
            main_task = progress.add_task("[cyan]🕸️ Scraping & Writing to Disk...", total=estimated_total_calls)
            
            for cat in categories:
                task = process_category(session, cat, page_size, semaphore, all_links, progress, main_task)
                tasks.append(task)
                
            await asyncio.gather(*tasks)

    rprint("\n" + "="*60)
    rprint(f"[bold green]🎉 FULL CATALOG EXTRACTED! All safely written to '{OUTPUT_FILE}'.[/bold green]")
    rprint("="*60 + "\n")

if __name__ == "__main__":
    if os.name == 'nt':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main_async_scraper())