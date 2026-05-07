import requests
import json
from rich import print as rprint

def get_total_inventory_and_categories():
    # q=* ka matlab hai "Mera bhai sab kuch le aao, koi filter mat lagao"
    # rows=0 kiya hai kyunki hume sirf counts aur categories chahiye, products nahi
    api_url = "https://search.unbxd.io/2f0815a68672fd25b4b7992b72302e5b/ss-unbxd-aapac-prod-sencogold56671721125516/search?q=*&rows=0"
    
    response = requests.get(api_url)
    data = response.json()
    
    # 1. Total Website Products Count
    total_products = data.get('response', {}).get('numberOfProducts', 0)
    rprint(f"\n[bold green]💰 TOTAL PRODUCTS ON SENCO WEBSITE: {total_products}[/bold green]\n")
    
    # 2. Extracting Categories and Their Exact Counts
    facets = data.get('facets', {}).get('text', {}).get('list', [])
    
    for facet in facets:
        if facet.get('facetName') == 'categoryPath2_uFilter': # Main Categories
            values = facet.get('values', [])
            
            rprint("[bold cyan]📊 EXACT CATEGORY COUNTS:[/bold cyan]")
            # Unbxd API values aise bhejti hai: ["Rings", 2500, "Chains", 1000]
            for i in range(0, len(values), 2):
                category_name = values[i]
                category_count = values[i+1]
                print(f" -> {category_name}: {category_count} items")

if __name__ == "__main__":
    get_total_inventory_and_categories()