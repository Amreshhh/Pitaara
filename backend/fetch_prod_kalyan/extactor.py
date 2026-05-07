import asyncio
import json
import os
import sys
import re
from datetime import datetime
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

from utils import get_formatted_date, detect_category, check_if_diamond, infer_missing_purity

# 🔥 GLOBAL LOCK FOR LIVE SAVING
file_lock = asyncio.Lock()
LIVE_OUTPUT_FILE = "candere_live_temp.jsonl"
FINAL_OUTPUT_FILE = "candere_finals_data.json"

# ==========================================
# 💾 LIVE SAVER
# ==========================================
async def save_product_on_the_fly(product_data):
    """Safely appends a single product to the JSONL file."""
    async with file_lock:
        with open(LIVE_OUTPUT_FILE, 'a', encoding='utf-8') as f:
            f.write(json.dumps(product_data, ensure_ascii=False) + '\n')

# ==========================================
# 🚀 CORE API EXTRACTOR
# ==========================================
async def process_single_product(session, item, sem, progress, task_id):
    sku = item.get("sku")
    product_url = item.get("url")
    title = item.get("name", "")
    
    api_url = f"https://www.candere.com/JewelleryProduct/product/getCustomDesignPricing/?product_id={sku}&pincode=400001&purity_id=18k"
    
    async with sem:
        try:
            response = await session.get(api_url, impersonate="chrome110", timeout=20)
            
            if response.status_code != 200:
                progress.update(task_id, advance=1)
                return False
                
            data = response.json()
            
            # 1. Weights Extraction & Math
            gross_weight = float(data.get("total_weight", 0.0))
            stone_weight_carat = float(data.get("total_stone_weight", 0.0))
            net_weight = round(gross_weight - (stone_weight_carat * 0.2), 3) # 1 Carat = 0.2g
            if net_weight <= 0: net_weight = gross_weight
            
            # 2. Price & Making Charge Math
            metal_price = float(data.get("metal_price", 0.0))
            
            # 🔥 NEW FALLBACK LOGIC HERE 🔥
            # Pehle discount dhundega, agar falsy hai (None ya 0) toh making_charge uthayega
            actual_mc = data.get("discount_making_charge")
            if not actual_mc: 
                actual_mc = data.get("making_charge", 0.0)
            actual_mc = float(actual_mc)
            
            stone_charges = float(data.get("stone_price", 0.0))
            
            mc_percentage_str = "0 %"
            if metal_price > 0 and actual_mc > 0:
                mc_pct = (actual_mc / metal_price) * 100
                mc_percentage_str = f"{round(mc_pct, 2)} %"
                
            # 3. Purity Extraction
            purity = "Unknown"
            if data.get("metal") and len(data["metal"]) > 0:
                purity = data["metal"][0].get("purity", "Unknown")
                
            # 4. Utilities Application
            breakup_for_utils = {
                "purity": purity,
                "stone_charges": stone_charges
            }
            
            final_type = check_if_diamond(title + " " + product_url, breakup_for_utils)
            final_category = detect_category(title + " " + product_url)
            
            # 🚀 STEP 4.5: PURITY INFERENCE (NEW)
            # Agar purity "Unknown" hai, toh metal_price aur net_weight se infer karna
            inferred_purity = purity
            if purity == "Unknown" and metal_price > 0 and net_weight > 0:
                try:
                    # Fallback live rates for Candere (approximate)
                    # These can be updated by fetching from connection/live_rates.py
                    live_rates_cache = {
                        "24K": 7500,
                        "22K": 6875,
                        "18K": 5625,
                        "14K": 4375
                    }
                    
                    item_for_inference = {
                        "gold_value": metal_price,
                        "net_weight": net_weight
                    }
                    
                    inferred_purity = infer_missing_purity(item_for_inference, live_rates_cache)
                except Exception as e:
                    # Agar inference fail ho toh original rakhna
                    pass
            
            # 5. Final Assembly
            final_product = {
                "Brand": "Candere",
                "product_url": product_url,
                "sku": str(sku),
                "type": final_type,
                "purity": inferred_purity,  # 🚀 Now can be inferred
                "net_weight": net_weight,
                "making_charges_percentage": mc_percentage_str,
                "category": final_category,
                "extraction_date": get_formatted_date()
            }
            
            # Save instantly to disk
            await save_product_on_the_fly(final_product)
            
            progress.update(task_id, advance=1)
            return True
            
        except Exception as e:
            progress.update(task_id, advance=1)
            return False

# ==========================================
# ⚙️ MAIN ORCHESTRATOR
# ==========================================
async def main():
    INPUT_FILE = "candere_finals.json"
    CONCURRENCY_LIMIT = 100
    
    console.print(Panel(f"[bold magenta]⚡ Candere Internal API Bulk Extractor[/bold magenta]", expand=False))
    
    try:
        with open(INPUT_FILE, "r", encoding="utf-8") as f:
            input_data = json.load(f)
            product_list = input_data.get("data", []) if isinstance(input_data, dict) else input_data
    except FileNotFoundError:
        console.print(f"[bold red][!] File {INPUT_FILE} not found.[/bold red]")
        return
        
    console.print(f"Loaded {len(product_list)} products for API extraction...")
    
    if os.path.exists(LIVE_OUTPUT_FILE):
        os.remove(LIVE_OUTPUT_FILE)
        
    sem = asyncio.Semaphore(CONCURRENCY_LIMIT)
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console
    ) as progress:
        
        task_id = progress.add_task("[cyan]Processing via Candere Backend API...", total=len(product_list))
        
        async with AsyncSession() as session:
            tasks = []
            for item in product_list:
                tasks.append(process_single_product(session, item, sem, progress, task_id))
            
            await asyncio.gather(*tasks)

    # Convert JSONL to Final Array JSON
    console.print("\n[cyan]Packaging data into final JSON array...[/cyan]")
    final_master_array = []
    
    if os.path.exists(LIVE_OUTPUT_FILE):
        with open(LIVE_OUTPUT_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                final_master_array.append(json.loads(line.strip()))
                
        with open(FINAL_OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(final_master_array, f, indent=4, ensure_ascii=False)
            
        os.remove(LIVE_OUTPUT_FILE)
            
    console.print(Panel(
        f"[bold green]Data Pipeline Execution Successful![/bold green]\n"
        f"Products Safely Extracted: [bold cyan]{len(final_master_array)}[/bold cyan]\n"
        f"Final Output File: [bold yellow]{FINAL_OUTPUT_FILE}[/bold yellow]",
        title="[bold blue]Final Report[/bold blue]"
    ))

if __name__ == "__main__":
    import sys
    if sys.platform.startswith('win'):
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())