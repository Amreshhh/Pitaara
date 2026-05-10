#!/usr/bin/env python3
"""
🔍 DEBUG SCRIPT: Check MongoDB collections and data
Run this to diagnose why the frontend shows "N/A" for prices
"""

import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = "jewelry_database"

async def debug_mongo():
    print("=" * 60)
    print("🔍 MONGODB DEBUG SCRIPT")
    print("=" * 60)
    print(f"\n📍 Connecting to: {MONGO_URI}")
    print(f"📍 Database: {DB_NAME}\n")
    
    try:
        client = AsyncIOMotorClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        db = client[DB_NAME]
        
        # Test connection
        await client.admin.command("ping")
        print("✅ MongoDB connection successful!\n")
        
        # List all collections
        collections = await db.list_collection_names()
        print(f"📊 Collections in '{DB_NAME}':")
        if collections:
            for i, col in enumerate(collections, 1):
                print(f"   {i}. {col}")
        else:
            print("   ❌ NO COLLECTIONS FOUND!")
        
        # Check specific collections the API is looking for
        print("\n🔎 Checking for API collections:")
        expected_collections = [
            "malabar_products",
            "kalyan_products", 
            "tanishq_products",
            "senco_products",
            "live_rates_cache",
            "candere_products"  # Alternative name for Kalyan
        ]
        
        for col_name in expected_collections:
            if col_name in collections:
                count = await db[col_name].count_documents({})
                print(f"   ✅ {col_name}: {count} documents")
                
                # Show sample document
                if count > 0:
                    sample = await db[col_name].find_one({})
                    keys = list(sample.keys())[:5]  # First 5 keys
                    print(f"      Sample keys: {keys}")
            else:
                print(f"   ❌ {col_name}: NOT FOUND")
        
        # Check for any collection with 'product' in name
        print("\n🔍 Collections with 'product' in name:")
        product_cols = [c for c in collections if 'product' in c.lower()]
        if product_cols:
            for col in product_cols:
                count = await db[col].count_documents({})
                print(f"   {col}: {count} documents")
        else:
            print("   None found")
        
        # Check live rates cache
        print("\n💰 Live Rates Cache:")
        if "live_rates_cache" in collections:
            rates = await db["live_rates_cache"].find_one({})
            if rates:
                print(f"   ✅ Cache exists with keys: {list(rates.keys())}")
                if "rates" in rates:
                    print(f"   Rates data: {rates['rates']}")
            else:
                print("   ❌ Cache collection exists but empty")
        else:
            print("   ❌ Cache collection not found")
        
        # Sample data from first collection with products
        if product_cols:
            first_col = db[product_cols[0]]
            count = await first_col.count_documents({})
            if count > 0:
                print(f"\n📄 Sample from {product_cols[0]}:")
                sample = await first_col.find_one({})
                # Print first few fields
                for key in list(sample.keys())[:8]:
                    print(f"   {key}: {sample[key]}")
        
        client.close()
        print("\n" + "=" * 60)
        print("✅ Debug complete")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_mongo())
