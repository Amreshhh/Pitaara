import xml.etree.ElementTree as ET
from curl_cffi import requests
from rich.console import Console

console = Console()

def count_sitemap_products():
    # Saare main product sitemaps
    sitemaps = [
        "https://www.candere.com/media/sitemap_category/sitemap_product.xml",
        "https://www.candere.com/media/sitemap_category/sitemap_platinum.xml",
        "https://www.candere.com/media/sitemap_category/sitemap_gold.xml",
        "https://www.candere.com/media/sitemap_category/sitemap_diamond.xml"
    ]

    all_unique_links = set()
    ns = {'sm': 'http://www.sitemaps.org/schemas/sitemap/0.9'}

    console.print("[bold magenta]🔍 Investigating Candere Sitemaps...[/bold magenta]\n")

    for url in sitemaps:
        try:
            response = requests.get(url, impersonate="chrome110", timeout=30)
            
            if response.status_code == 200:
                root = ET.fromstring(response.content)
                
                # Extract all URLs
                current_count = 0
                for loc in root.findall('.//sm:loc', ns):
                    if loc.text and ".html" in loc.text:
                        all_unique_links.add(loc.text)
                        current_count += 1
                        
                filename = url.split('/')[-1]
                console.print(f"[green]✓ {filename}[/green] -> {current_count} links found")
            else:
                console.print(f"[red]✗ Failed to load {url} (Status: {response.status_code})[/red]")
                
        except Exception as e:
            console.print(f"[red]✗ Error on {url}: {e}[/red]")

    console.print(f"\n[bold cyan]=======================================[/bold cyan]")
    console.print(f"[bold yellow]🏆 FINAL UNIQUE PRODUCT COUNT: {len(all_unique_links)}[/bold yellow]")
    console.print(f"[bold cyan]=======================================[/bold cyan]")

if __name__ == "__main__":
    count_sitemap_products()