import os
import json
import asyncio
import re
import urllib.parse
from curl_cffi.requests import AsyncSession
from rich import print as rprint
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn

# 🚀 CONFIGURATION
# Yahan tum apna koi bhi Malabar Category URL daal sakte ho
TARGET_URL = "https://www.malabargoldanddiamonds.com/in/pan-india/en/product-list/necklace.html?category_uid=MTA=&malabar_product_type=72"
OUTPUT_FILE = "malabar_all_19k_links.json"

def format_url_name(name):
    clean = re.sub(r'[^a-zA-Z0-9\s-]', '', name).strip().lower()
    return re.sub(r'\s+', '-', clean)

async def main():
    rprint("\n[bold magenta]==========================================[/bold magenta]")
    rprint("[bold magenta] 🎯 MALABAR SINGLE-CATEGORY DEEP DIVE HARVESTER [/bold magenta]")
    rprint("[bold magenta]==========================================[/bold magenta]\n")

    # -----------------------------------------------------
    # 1. EXTRACT CATEGORY UID FROM TARGET URL
    # -----------------------------------------------------
    parsed_url = urllib.parse.urlparse(TARGET_URL)
    query_params = urllib.parse.parse_qs(parsed_url.query)
    category_uid = query_params.get("category_uid", [None])[0]

    if not category_uid:
        rprint("[bold red]❌ Error: No 'category_uid' found in TARGET_URL. Make sure it looks like ?category_uid=XYZ[/bold red]")
        return

    rprint(f"[cyan]🔍 Target Category UID detected:[/cyan] [bold yellow]{category_uid}[/bold yellow]")

    # -----------------------------------------------------
    # 2. LOAD EXISTING DATABASE
    # -----------------------------------------------------
    all_final_products = []
    unique_skus = set()

    if os.path.exists(OUTPUT_FILE):
        try:
            with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
                existing_data = json.load(f)
                all_final_products.extend(existing_data)
                for item in existing_data:
                    if item.get("sku"): unique_skus.add(item["sku"])
            rprint(f"[green]📂 Loaded {len(unique_skus)} existing SKUs from '{OUTPUT_FILE}'.[/green]\n")
        except Exception: 
            pass

    initial_count = len(unique_skus)

    # -----------------------------------------------------
    # 3. QUERY MAGENTO GRAPHQL API FOR THIS CATEGORY
    # -----------------------------------------------------
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

    headers = {
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Referer": "https://www.malabargoldanddiamonds.com/",
    }

    page_size = 100
    current_page = 1
    total_pages = 1 # Update hoga pehli request ke baad

    async with AsyncSession(headers=headers) as session:
        rprint("[yellow]🔄 Scanning pages for new products...[/yellow]")
        
        with Progress(
            SpinnerColumn("dots", style="cyan"),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(complete_style="green", finished_style="green"),
            TaskProgressColumn()
        ) as progress:
            
            # Shuru mein hume total pages nahi pata, toh task setup karenge
            task = progress.add_task(f"[cyan]Paginating Category... (Total: {len(unique_skus)})", total=None)

            while current_page <= total_pages:
                variables_dict = {
                    "pageSize": page_size,
                    "currentPage": current_page,
                    "filter": { "category_uid": { "in": [category_uid] } }
                }
                params = { "query": graphql_query, "variables": json.dumps(variables_dict) }

                try:
                    response = await session.get(api_url, params=params, impersonate="chrome120", timeout=20)
                    if response.status_code != 200:
                        break

                    data = response.json()
                    products_data = data.get("data", {}).get("products", {})
                    
                    # 🚀 Update progress bar total on first pass
                    if current_page == 1:
                        total_pages = products_data.get("page_info", {}).get("total_pages", 1)
                        progress.update(task, total=total_pages)

                    items = products_data.get("items", [])
                    if not items: break

                    # 🚀 TRACKERS FOR THIS SPECIFIC PAGE
                    parsed_this_page = len(items)
                    new_added_this_page = 0

                    for item in items:
                        sku = item.get("sku")
                        
                        # 🛑 STRICT DUPLICATE CHECK (Senco Style)
                        if sku and sku not in unique_skus:
                            unique_skus.add(sku)
                            new_added_this_page += 1
                            name = item.get("name", "malabar-product")
                            
                            barcode = ""
                            breakup = item.get("price_breakup")
                            if breakup and isinstance(breakup, list) and len(breakup) > 0:
                                barcode = breakup[0].get("barcode", "")
                            elif isinstance(breakup, dict):
                                 barcode = breakup.get("barcode", "")

                            formatted_name = format_url_name(name)
                            product_url = f"https://www.malabargoldanddiamonds.com/in/pan-india/en/product/{formatted_name}.html?sku={sku}&barcode={barcode}"

                            all_final_products.append({
                                "sku": sku,
                                "name": name,
                                "product_url": product_url
                            })
                    
                    # 🚀 REAL-TIME PRINTING IN TERMINAL
                    progress.console.print(f"[white]📄 Page {current_page}/{total_pages}[/white] | [cyan]Parsed: {parsed_this_page}[/cyan] | [green]New Added: {new_added_this_page}[/green] | [yellow]Total DB: {len(unique_skus)}[/yellow]")
                    
                    progress.update(task, advance=1, description=f"[cyan]Paginating Category... (Total DB: {len(unique_skus)})")
                    current_page += 1
                    
                    await asyncio.sleep(0.5) # API ko saans lene do (Anti-ban)

                except Exception as e:
                    progress.console.print(f"[red]⚠️ Error on page {current_page}: {e}[/red]")
                    break

    # -----------------------------------------------------
    # 4. FINAL REPORT & SAVE
    # -----------------------------------------------------
    new_items = len(unique_skus) - initial_count
    
    if new_items > 0:
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(all_final_products, f, indent=4)
            
    rprint("\n[bold green]==========================================[/bold green]")
    rprint(f"[bold white on green] 🎉 SCAN COMPLETE! Found and Saved {new_items} NEW items. [/bold white on green]")
    rprint(f"[cyan] 📦 Total Products now in DB: {len(all_final_products)} [/cyan]")
    rprint("[bold green]==========================================[/bold green]\n")

if __name__ == "__main__":
    if os.name == 'nt':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())