import json
import os
from rich.console import Console
from rich.table import Table

console = Console()

def print_json_as_table(filepath):
    # Check if file exists
    if not os.path.exists(filepath):
        console.print(f"[bold red]Bhai, {filepath} file nahi mili![/bold red]")
        return

    # Load JSON data
    with open(filepath, 'r', encoding='utf-8') as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            console.print(f"[bold red]JSON format me error hai {filepath} me![/bold red]")
            return
    
    if not data:
        console.print("[yellow]JSON file empty hai.[/yellow]")
        return

    # 🔥 SORTING LOGIC 🔥
    # Priority: 0 for Gold, 1 for Diamond, 2 for the rest
    def get_sort_priority(item):
        item_type = str(item.get("type", ""))
        if item_type == "Gold (Scraped)":
            return 0
        elif item_type == "Diamond (Scraped)":
            return 1
        else:
            return 2

    # Data ko sort karo
    sorted_data = sorted(data, key=get_sort_priority)

    # Table setup karo
    table = Table(title="Sorted Product Extraction Data", show_header=True, header_style="bold white")
    
    # Columns add karo
    table.add_column("SKU", style="cyan", no_wrap=True)
    table.add_column("Category", style="yellow")
    table.add_column("Type", style="blue")
    table.add_column("Making Rate", style="magenta")
    table.add_column("Discount Label", style="green")

    # Sorted data ko table me feed karo
    for item in sorted_data:
        sku = str(item.get("sku", "N/A"))
        category = str(item.get("category", "N/A"))
        item_type = str(item.get("type", "N/A"))
        making_rate = str(item.get("making_rate", "N/A"))
        discount = str(item.get("discount_label", "N/A"))
        
        table.add_row(sku, category, item_type, making_rate, discount)

    # Table Print karo
    console.print(table)
    
    # 🔥 TOTAL ENTRIES PRINT 🔥
    console.print(f"\n[bold green]Total Entries Printed: {len(sorted_data)}[/bold green]")

if __name__ == "__main__":
    # Apni JSON file ka naam confirm kar lena
    JSON_FILE = "candere_making_rates_and_details.json" 
    print_json_as_table(JSON_FILE)