import os
import json
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, BulkWriteError
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel

console = Console()

def push_data_to_mongodb(json_file_path):
    # 1. Load environment variables from .env file
    load_dotenv()
    mongo_uri = os.getenv("MONGO_URI")
    
    if not mongo_uri:
        console.print("[bold red][!] Error: MONGO_URI not found in .env file.[/bold red]")
        return

    # 2. Database and Collection Setup
    # Image ke hisaab se aapka database 'jewelry_database' hai
    DB_NAME = "jewelry_database" 
    COLLECTION_NAME = "kalyan_products"

    try:
        console.print("[cyan]Connecting to MongoDB Cluster...[/cyan]")
        client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
        
        # Test connection
        client.admin.command('ping')
        console.print("[bold green]Successfully connected to MongoDB![/bold green]")
        
        db = client[DB_NAME]
        collection = db[COLLECTION_NAME]
        
    except ConnectionFailure:
        console.print("[bold red]Failed to connect to MongoDB. Please check your MONGO_URI or internet connection.[/bold red]")
        return

    # 3. Read JSON File
    try:
        console.print(f"[cyan]Reading data from {json_file_path}...[/cyan]")
        with open(json_file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            
            # Agar data dictionary format me hai (jaise {"data": [...]}), toh use array me convert karo
            if isinstance(data, dict):
                # Using 'data' key if it exists, otherwise wrapping the dict in a list
                records_to_insert = data.get("data", [data])
            else:
                records_to_insert = data

    except FileNotFoundError:
        console.print(f"[bold red]File {json_file_path} not found![/bold red]")
        return
    except json.JSONDecodeError:
        console.print(f"[bold red]Invalid JSON format in {json_file_path}![/bold red]")
        return

    # 4. Insert Data into MongoDB
    if not records_to_insert:
        console.print("[yellow]JSON file is empty. Nothing to insert.[/yellow]")
        return

    try:
        console.print(f"[cyan]Pushing {len(records_to_insert)} records to '{COLLECTION_NAME}' collection...[/cyan]")
        result = collection.insert_many(records_to_insert)
        
        # 5. Success Message
        console.print(Panel(
            f"[bold green]Data Push Successful![/bold green]\n"
            f"Database: [bold yellow]{DB_NAME}[/bold yellow]\n"
            f"Collection: [bold yellow]{COLLECTION_NAME}[/bold yellow]\n"
            f"Total Documents Inserted: [bold cyan]{len(result.inserted_ids)}[/bold cyan]",
            title="[bold blue]MongoDB Status[/bold blue]"
        ))

    except BulkWriteError as bwe:
        console.print("[bold red]Error occurred while inserting documents (e.g., duplicate IDs).[/bold red]")
        console.print(bwe.details)
    except Exception as e:
        console.print(f"[bold red]An unexpected error occurred: {e}[/bold red]")
    finally:
        client.close()

if __name__ == "__main__":
    # Yahan apni kalyan products wali JSON file ka exact path daal dena
    JSON_FILE = "candere_finals_data.json" 
    push_data_to_mongodb(JSON_FILE)