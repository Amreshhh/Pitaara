import json
import os
from rich.console import Console
from rich.panel import Panel

console = Console()

# ====================================================
# 🎯 APNI JSON FILES KA NAAM YAHAN DAALEIN
# ====================================================
INPUT_FILES = [
    "candere_master_rings.json",
    "candere_master_all_categories.json",
    "candere_senco_method_master.json",
    "candere_full_catalog_master.json",
    "candere_FINAL_MASTER_DATABASE.json",
    "candere_all_links.json"
    # "koi_bhi_file.json" add karte jao
]

OUTPUT_FILE = "candere_finals.json"

def merge_and_deduplicate(file_list):
    console.print(Panel("[bold magenta]🛠️ Data Merger & Deduplicator[/bold magenta]", expand=False))
    
    unique_products = {} # Dictionary: key=sku, value=product_data
    total_duplicates_found = 0
    total_files_processed = 0

    for filename in file_list:
        if not os.path.exists(filename):
            console.print(f"[red][!] File not found: {filename} (Skipping)[/red]")
            continue
            
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                file_content = json.load(f)
                
                # Check format: Agar data "data" key ke andar hai (Jo humne pehle scripts mein banaya tha)
                if isinstance(file_content, dict) and "data" in file_content:
                    products = file_content["data"]
                elif isinstance(file_content, list):
                    # Agar seedha list of products hai
                    products = file_content
                else:
                    console.print(f"[yellow][!] Unknown format in {filename}. Skipping.[/yellow]")
                    continue
                
                new_in_this_file = 0
                duplicates_in_this_file = 0
                
                for item in products:
                    sku = item.get('sku') or item.get('id') # SKU nikalna
                    
                    if not sku:
                        continue # Agar SKU hi nahi hai toh ignore karo
                        
                    if sku in unique_products:
                        duplicates_in_this_file += 1
                        total_duplicates_found += 1
                    else:
                        # Naya product dictionary mein add karo
                        unique_products[sku] = item
                        new_in_this_file += 1
                
                console.print(f"[green]✓ Processed {filename}:[/green] Added {new_in_this_file} new, Ignored {duplicates_in_this_file} duplicates.")
                total_files_processed += 1
                
        except Exception as e:
            console.print(f"[bold red][!] Error reading {filename}: {e}[/bold red]")

    # ==========================================
    # FINAL SAVE
    # ==========================================
    if unique_products:
        # Dictionary ki values ko wapas list mein convert karna
        final_product_list = list(unique_products.values())
        
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump({
                "source_files_merged": total_files_processed,
                "total_unique_products": len(final_product_list),
                "total_duplicates_removed": total_duplicates_found,
                "data": final_product_list
            }, f, indent=4)
            
        console.print(Panel(
            f"[bold green]Merging Successful![/bold green]\n"
            f"Files Processed: [bold cyan]{total_files_processed}[/bold cyan]\n"
            f"Duplicates Destroyed: [bold red]{total_duplicates_found}[/bold red]\n"
            f"Total Unique Products in Master: [bold yellow]{len(final_product_list)}[/bold yellow]\n"
            f"Saved to: [bold cyan]{OUTPUT_FILE}[/bold cyan]",
            title="[bold blue]Final Report[/bold blue]"
        ))
    else:
        console.print("[bold red][!] No valid data found across all files.[/bold red]")

if __name__ == "__main__":
    merge_and_deduplicate(INPUT_FILES)