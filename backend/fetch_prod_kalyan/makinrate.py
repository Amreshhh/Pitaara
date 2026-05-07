import asyncio
import json
from curl_cffi.requests import AsyncSession
from rich.console import Console
from rich.progress import track
from rich.table import Table

console = Console()

# ==========================================
# 🚀 UTILS LOGIC (Category & Type Classifier)
# ==========================================
def detect_category(name_or_url):
    if not name_or_url: return "Other"
    lower_name = name_or_url.lower()
    
    if any(word in lower_name for word in ['earring', 'jhumka', 'stud', 'drops']): return "Earring"
    if any(word in lower_name for word in ['bali', 'hoops']): return "Bali"
    if 'ring' in lower_name: return "Ring"
    if 'choker' in lower_name: return "Choker"
    if any(word in lower_name for word in ['necklace', 'neckwear']): return "Necklace"
    if 'chain' in lower_name: return "Chain"
    if 'bangle' in lower_name: return "Bangles"
    if 'bracelet' in lower_name: return "Bracelet"
    if 'kada' in lower_name: return "Kada"
    if 'coin' in lower_name: return "Gold Coin"
    if 'set' in lower_name: return "Set"
    if 'pendant' in lower_name: return "Pendant"
    if 'mangalsutra' in lower_name: return "Mangalsutra"
    if 'nose' in lower_name: return "Nose Pin"
    if 'nath' in lower_name: return "Nath"
    if any(word in lower_name for word in ['anklet', 'payal']): return "Anklet"
    
    return "Other"

def check_if_diamond(name_or_url, breakup_dict):
    text_lower = name_or_url.lower() if name_or_url else ""
    purity_lower = str(breakup_dict.get("purity", "Unknown")).lower()
    
    has_solitaire_in_text = 'solitaire' in text_lower
    has_diamond_in_text = 'diamond' in text_lower or 'stone' in text_lower
    has_platinum_in_text = 'platinum' in text_lower
    has_silver_in_text = 'silver' in text_lower
    
    try:
        total_stone = float(breakup_dict.get('stone_charges', 0))
        has_stone_charges = total_stone > 2000
    except:
        has_stone_charges = False
        
    is_studded_diamond = has_diamond_in_text 
    is_studded_stone = has_stone_charges
    
    detailed_type = "Gold (Scraped)"
    
    if has_platinum_in_text:
        if is_studded_diamond: detailed_type = "Platinum & Diamond (Scraped)"
        elif is_studded_stone: detailed_type = "Platinum & Stone (Scraped)"
        elif has_solitaire_in_text: detailed_type = "Platinum Solitaire (Scraped)"
        else: detailed_type = "Platinum (Scraped)"
    elif is_studded_diamond: detailed_type = "Diamond (Scraped)"
    elif is_studded_stone: detailed_type = "Stone (Scraped)"
    elif has_solitaire_in_text: detailed_type = "Solitaire (Scraped)"
    elif has_silver_in_text: detailed_type = "Silver (Scraped)"

    if 'silver' in purity_lower and 'gold' in detailed_type.lower():
        detailed_type = detailed_type.replace("Gold", "Silver")
    elif ('gold' in purity_lower or 'k' in purity_lower) and 'silver' in detailed_type.lower():
        if 'gold' in purity_lower:
            detailed_type = detailed_type.replace("Silver", "Gold")

    return detailed_type

# ==========================================
# 🚀 CORE EXTRACTOR
# ==========================================
async def fetch_all_details(session, item, sem):
    sku = item.get("sku")
    product_url = item.get("url", "")
    title = item.get("name", "")
    
    if not sku:
        return None
        
    api_url = f"https://www.candere.com/JewelleryProduct/product/getCustomDesignPricing/?product_id={sku}&pincode=400001&purity_id=18k"
    
    async with sem:
        try:
            response = await session.get(api_url, impersonate="chrome110", timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                
                # 1. Extraction: Making Rate & Discount
                making_rate = data.get("making_rate", 0.0)
                discount_label = data.get("discount_label") or data.get("offer_message") or data.get("discount_text", "No Discount Label")
                
                # 2. Purity & Stone Charges for Classifier
                stone_charges = float(data.get("stone_price", 0.0))
                purity = "Unknown"
                if data.get("metal") and len(data["metal"]) > 0:
                    purity = data["metal"][0].get("purity", "Unknown")
                    
                breakup_for_utils = {
                    "purity": purity,
                    "stone_charges": stone_charges
                }
                
                # 3. Classify Type & Category
                combo_text = title + " " + product_url
                final_type = check_if_diamond(combo_text, breakup_for_utils)
                final_category = detect_category(combo_text)
                
                return {
                    "sku": str(sku),
                    "product_url": product_url,
                    "making_rate": float(making_rate),
                    "discount_label": str(discount_label),
                    "category": final_category,
                    "type": final_type
                }
            return None
        except Exception as e:
            return None

# ==========================================
# ⚙️ MAIN ORCHESTRATOR
# ==========================================
async def main():
    INPUT_FILE = "candere_finals.json"
    OUTPUT_FILE = "candere_making_rates_and_details.json"
    CONCURRENCY_LIMIT = 100  

    try:
        with open(INPUT_FILE, "r", encoding="utf-8") as f:
            input_data = json.load(f)
            product_list = input_data.get("data", []) if isinstance(input_data, dict) else input_data
    except FileNotFoundError:
        console.print(f"[bold red]Input file {INPUT_FILE} missing![/bold red]")
        return

    console.print(f"[bold cyan]Starting extraction for {len(product_list)} products...[/bold cyan]")
    
    results = []
    sem = asyncio.Semaphore(CONCURRENCY_LIMIT)
    
    async with AsyncSession() as session:
        tasks = [fetch_all_details(session, item, sem) for item in product_list]
        
        for task in track(asyncio.as_completed(tasks), total=len(tasks), description="Extracting..."):
            result = await task
            if result:
                results.append(result)

    # Output file save karna
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4)
        
    console.print(f"\n[bold green]Success! Extracted making_rate, discounts, categories & types for {len(results)} items.[/bold green]")
    console.print(f"Saved to -> [bold yellow]{OUTPUT_FILE}[/bold yellow]\n")

    # Console me table setup karna
    table = Table(title="Sample Extracted Data")
    table.add_column("SKU", style="cyan", no_wrap=True)
    table.add_column("Category", style="yellow")
    table.add_column("Type", style="blue")
    table.add_column("Making Rate", style="magenta")
    table.add_column("Discount Label", style="green")

    # Shuru ke 10 items print karna
    for item in results[:10]:
        table.add_row(
            item["sku"], 
            item["category"], 
            item["type"], 
            str(item["making_rate"]), 
            item["discount_label"]
        )
        
    console.print(table)

if __name__ == "__main__":
    import sys
    if sys.platform.startswith('win'):
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())