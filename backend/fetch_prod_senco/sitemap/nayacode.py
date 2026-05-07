import asyncio
import json
from curl_cffi.requests import AsyncSession
from selectolax.parser import HTMLParser
from rich import print as rprint
import urllib.parse

# Tumhari target categories Senco ki website se
CATEGORIES = [
    "rings", "earrings", "pendants", "bangles", 
    "necklaces", "chains", "mangalsutras", "bracelets"
]

async def fetch_category_page(session, category, page):
    """Ek single page ko fetch aur parse karta hai selectolax ke saath"""
    url = f"https://sencogoldanddiamonds.com/jewellery/{category}?page={page}"
    
    try:
        response = await session.get(url, impersonate="chrome120", timeout=15)
        if response.status_code != 200:
            return None
            
        # 🚀 THE SELECTOLAX MAGIC (Bye Bye BeautifulSoup)
        tree = HTMLParser(response.text)
        
        # Product links dhoondne ka fast CSS selector
        links = tree.css('a[href*="/product/"]')
        
        extracted_products = []
        for node in links:
            href = node.attributes.get('href')
            if href:
                full_url = urllib.parse.urljoin("https://sencogoldanddiamonds.com", href)
                
                # Basic SKU extraction from URL (Optional, but good for DB)
                # Senco URLs look like: /product/gold-ring-12345SKU
                sku = full_url.split('-')[-1] if '-' in full_url else "Unknown"
                
                extracted_products.append({
                    "Brand": "Senco",
                    "product_url": full_url,
                    "sku": sku,
                    "category": category.capitalize()
                })
                
        return extracted_products
        
    except Exception as e:
        # rprint(f"[red]Error fetching {url}: {e}[/red]")
        return None

async def harvest_grid():
    rprint("\n[bold blue]🚀 Starting Async HTML Grid Harvester (Selectolax)...[/bold blue]")
    
    all_hybrid_products = []
    unique_urls = set()
    
    # 50 connections ek saath kholne ka limit
    semaphore = asyncio.Semaphore(50) 
    
    async with AsyncSession() as session:
        for category in CATEGORIES:
            rprint(f"\n[cyan]📂 Scraping Category: {category}[/cyan]")
            
            # Hum assume kar rahe hain ki ek category mein max 100 pages honge.
            # Tum isko bada sakte ho agar aur pages fetch karne hain.
            page = 1
            consecutive_empty_pages = 0
            
            while consecutive_empty_pages < 3: # Agar lagatar 3 pages khali aaye, toh agli category par jao
                # Ek baar mein 5 pages concurrently fetch karenge (Batching)
                tasks = []
                for p in range(page, page + 5):
                    tasks.append(fetch_category_page(session, category, p))
                
                results = await asyncio.gather(*tasks)
                
                batch_had_data = False
                for result_list in results:
                    if result_list and len(result_list) > 0:
                        batch_had_data = True
                        for item in result_list:
                            if item["product_url"] not in unique_urls:
                                unique_urls.add(item["product_url"])
                                all_hybrid_products.append(item)
                
                if batch_had_data:
                    rprint(f"✅ Fetched pages {page} to {page+4} | Total unique items so far: {len(unique_urls)}")
                    consecutive_empty_pages = 0
                else:
                    consecutive_empty_pages += 5
                    
                page += 5

    rprint(f"\n[bold green]🎉 HTML Grid Harvest Complete! Total Links: {len(all_hybrid_products)}[/bold green]")
    
    # Save the data
    with open("senco_grid_links.json", "w", encoding="utf-8") as f:
        json.dump(all_hybrid_products, f, indent=4)

if __name__ == "__main__":
    if __import__('os').name == 'nt':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(harvest_grid())