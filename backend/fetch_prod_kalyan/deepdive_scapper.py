import asyncio
import json
import os
import sys
from curl_cffi.requests import AsyncSession
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.panel import Panel

console = Console()

# ==========================================
# 🚀 UNIVERSAL UTILS INTEGRATION
# ==========================================
# Ye automatically 2 folders peeche jaakar utils ko dhoondhega 
# (Script -> fetch_prod_kalyan -> root_path)
root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

if root_path not in sys.path:
    sys.path.append(root_path)

from utils import detect_category, get_formatted_date

# Global Set for 'On The Fly' Duplicate Checking
seen_skus = set()
master_products = []

# =====================================================================
# 🎯 THE UPGRADED SENCO METHOD: EXACT MICRO-TARGETING
# Updated based on actual Candere Catalog Screenshots
# =====================================================================
DEEP_SUBCATEGORIES = [
    # 💍 RINGS
    "Engagement Rings", "Solitaire Rings", "Casual Rings", "Classic Rings", "Navratna Rings",
    "Mangalsutra Ring", "Couple Bands", "Eternity Ring", "Three Stone Rings",

    # ✨ EARRINGS
    "Stud Earrings", "Dangle Earrings", "Sui Dhaga Earrings", "Navratna Earrings",
    "Jhumkas", "Hoop Earrings", "Solitaire Earrings",

    # 📿 NECKLACES
    "Collar Necklace", "Layered Necklace", "Pendant Necklace", "Charm Necklace",
    "Delicate Necklace", "Lariat Necklace",

    # 💫 BANGLES & BRACELETS
    "Kada", "Delicate Bangles", "Oval Bracelets", "Tennis Bracelets",
    "Chain Bracelets", "Flexi Bracelets", "Eternity Bangles",

    # 🧿 MANGALSUTRA & PENDANTS
    "Mangalsutra with Chain", "Mangalsutra Bracelets", "Mangalsutra Chains", "Solitaire Mangalsutra",
    "Initial Pendants", "Solitaire Pendants", "Pendants with Chain", "Casual Pendants",

    # 🌟 FEATURED COLLECTIONS & ACCESSORIES
    "Peacock Collection", "Chafa Collection", "Butterfly Collection", "Evil Eye Collection",
    "Miracle Plate Collection", "Kyra Collection",
    "Nose Pin", "Watch Accessories", "Charms",

    # ⛓️ CHAINS
    "Dailywear Chains", "Fancy Chains", "Festive Chains", "Platinum Chains"
]

async def fetch_micro_category(session, search_term, progress, overall_task):
    api_url = "https://eucs27v2.ksearchnet.com/cs/v2/search"
    limit = 100
    offset = 0
    total_results = None
    
    # Har sub-category ke liye ek chhota progress bar
    task_id = progress.add_task(f"[cyan]Fetching '{search_term}'...", total=100)
    
    while True:
        payload = {
            "recordQueries": [{
                "id": "productSearch",
                "typeOfRequest": "SEARCH",
                "settings": {
                    "query": { "term": search_term },
                    "offset": offset,
                    "limit": limit,
                    "typeOfRecords": ["KLEVU_PRODUCT"]
                }
            }],
            "context": { "apiKeys": ["klevu-163066607292713309"] }
        }

        try:
            response = await session.post(api_url, json=payload, impersonate="chrome110", timeout=20)
            
            if response.status_code != 200:
                console.print(f"[red][!] API Error on {search_term}[/red]")
                break
                
            data = response.json()
            query_result = data.get('queryResults', [{}])[0]
            records = query_result.get('records', [])
            
            if total_results is None:
                total_results = query_result.get('meta', {}).get('totalResultsFound', 0)
                if total_results == 0:
                    progress.update(task_id, description=f"[dim]No items for '{search_term}'[/dim]", completed=100)
                    break
                progress.update(task_id, total=total_results)
            
            if not records:
                break
                
            # 🚀 Deduplication Magic (Checking SKU)
            new_additions = 0
            for item in records:
                sku = item.get('id')
                if sku not in seen_skus:
                    seen_skus.add(sku)
                    product_name = item.get('name', '')
                    
                    # 🚀 UTILS: Detect proper category from product name
                    detected_category = detect_category(product_name + " " + search_term)
                    
                    master_products.append({
                        "name": product_name,
                        "sku": sku,
                        "price": item.get('price'),
                        "url": item.get('url'),
                        "category": detected_category,  # 🚀 Proper category detection
                        "micro_category": search_term,
                        "extraction_date": get_formatted_date()  # 🚀 Timestamp added
                    })
                    new_additions += 1
            
            progress.update(task_id, advance=len(records))
            progress.update(overall_task, advance=new_additions)
            
            offset += limit
            if offset >= total_results:
                progress.update(task_id, description=f"[green]✓ '{search_term}' Done![/green]")
                break
                
            await asyncio.sleep(0.3)

        except Exception as e:
            console.print(f"[red][!] Error in {search_term}: {e}[/red]")
            break

async def main():
    console.print(Panel("[bold magenta]🎯 Senco Method V2: The Complete Catalog Sweeper[/bold magenta]", expand=False))
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console
    ) as progress:
        
        overall_task = progress.add_task("[bold yellow]Total Unique Products Found...", total=None)
        
        async with AsyncSession() as session:
            tasks = []
            for term in DEEP_SUBCATEGORIES:
                tasks.append(fetch_micro_category(session, term, progress, overall_task))
            
            # Fire all 40+ categories in parallel!
            await asyncio.gather(*tasks)
            
            progress.update(overall_task, description=f"[bold green]Mission Accomplished! Total Unique: {len(seen_skus)}[/bold green]")

    # Save Results
    output_file = "candere_full_catalog_master.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump({
            "extraction_method": "Senco Deep Dive V2",
            "total_unique": len(master_products),
            "data": master_products
        }, f, indent=4)
        
    console.print(Panel(
        f"[bold green]Data Pipeline Execution Successful![/bold green]\n"
        f"Micro-Categories Scanned: [bold cyan]{len(DEEP_SUBCATEGORIES)}[/bold cyan]\n"
        f"Total Unique Products Saved: [bold yellow]{len(master_products)}[/bold yellow]\n"
        f"Output File: [bold cyan]{output_file}[/bold cyan]",
        title="[bold blue]Final Report[/bold blue]"
    ))

if __name__ == "__main__":
    import sys
    if sys.platform.startswith('win'):
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())