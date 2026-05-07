import asyncio
import json
import time
from urllib.parse import urlparse
from curl_cffi.requests import AsyncSession
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.panel import Panel

console = Console()

# Global variables for "On the Fly" deduplication
seen_skus = set()
master_products_list = []

def extract_search_term(url):
    """URL se exact search term nikalta hai."""
    parsed_url = urlparse(url)
    filename = parsed_url.path.split('/')[-1]
    search_term = filename.replace('.html', '').replace('-', ' ').strip()
    return search_term

async def fetch_category(session, input_url, progress, overall_task):
    """Ek single category ko handle karta hai (Pagination ke saath)"""
    api_url = "https://eucs27v2.ksearchnet.com/cs/v2/search"
    search_term = extract_search_term(input_url)
    
    limit = 100
    offset = 0
    total_results = None
    
    # Har category ke liye ek sub-task (progress bar)
    category_task = progress.add_task(f"[cyan]Fetching {search_term.title()}...", total=100)
    
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
            # Async POST request
            response = await session.post(api_url, json=payload, impersonate="chrome110", timeout=20)
            
            if response.status_code != 200:
                console.print(f"[bold red][!] HTTP {response.status_code} on {search_term}[/bold red]")
                break
                
            data = response.json()
            query_result = data.get('queryResults', [{}])[0]
            records = query_result.get('records', [])
            
            # Pehli call par total items nikalna
            if total_results is None:
                total_results = query_result.get('meta', {}).get('totalResultsFound', 0)
                if total_results == 0:
                    progress.update(category_task, description=f"[bold red]No products for {search_term}[/bold red]")
                    break
                progress.update(category_task, total=total_results)
            
            if not records:
                break
            
            # ==========================================
            # 🚀 "ON THE FLY" DUPLICATE CHECKING
            # ==========================================
            added_in_this_batch = 0
            for item in records:
                sku = item.get('id')
                
                if sku not in seen_skus:
                    seen_skus.add(sku) # Set mein add karo
                    
                    master_products_list.append({
                        "name": item.get('name'),
                        "sku": sku,
                        "price": item.get('price'),
                        "url": item.get('url'),
                        "source_category": search_term.title()
                    })
                    added_in_this_batch += 1
            
            # Progress updates
            progress.update(category_task, advance=len(records))
            progress.update(overall_task, advance=added_in_this_batch) # Overall counter update
            
            offset += limit
            if offset >= total_results:
                progress.update(category_task, description=f"[green]✓ {search_term.title()} Complete![/green]")
                break
                
            await asyncio.sleep(0.5) # Async sleep taaki baaki requests block na hon

        except Exception as e:
            console.print(f"[bold red][!] Error in {search_term}: {e}[/bold red]")
            break

async def main(url_list):
    console.print(Panel("[bold magenta]🚀 Multi-Category Async Extractor[/bold magenta]", expand=False))
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console
    ) as progress:
        
        # Ek master progress bar jo total unique products dikhayega
        overall_task = progress.add_task("[bold yellow]Total Unique Products Extracted...", total=None)
        
        # AsyncSession se saari requests bhejen
        async with AsyncSession() as session:
            tasks = []
            for url in url_list:
                # Har URL ke liye ek background task create karo
                tasks.append(fetch_category(session, url, progress, overall_task))
            
            # Saare categories ko PARALLEL run karo!
            await asyncio.gather(*tasks)
            
            progress.update(overall_task, description=f"[bold green]Done! Total Unique: {len(seen_skus)}[/bold green]")

    # Final Data Saving
    output_file = "candere_master_all_categories.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump({
            "total_unique_products": len(master_products_list),
            "data": master_products_list
        }, f, indent=4)
        
    console.print(Panel(
        f"[bold green]Pipeline Execution Successful![/bold green]\n"
        f"Categories Processed: [bold cyan]{len(url_list)}[/bold cyan]\n"
        f"Total Unique Products Saved: [bold cyan]{len(master_products_list)}[/bold cyan]\n"
        f"Output File: [bold yellow]{output_file}[/bold yellow]",
        title="[bold blue]Final Report[/bold blue]"
    ))

if __name__ == "__main__":
    # ====================================================
    # 🎯 APNI SAARI LINKS YAHAN DAAL DO
    # ====================================================
    TARGET_URLS = [

        "https://www.candere.com/jewellery/rings.html",
        "https://www.candere.com/jewellery/earrings.html",
        "https://www.candere.com/jewellery/necklaces.html",
        "https://www.candere.com/jewellery/mangalsutra.html",
        "https://www.candere.com/jewellery/bangles-and-bracelets.html",
        "https://www.candere.com/trending/express-delivery.html",
       " https://www.candere.com/jewellery.html"
    # ]
    ]
    
    
    # Windows ke liye Async policy setup
    import sys
    if sys.platform.startswith('win'):
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        
    asyncio.run(main(TARGET_URLS))