#!/usr/bin/env python3
"""
🧪 TEST SCRIPT: Verify backend API is working
This tests:
1. Database connectivity
2. Cache bootstrapping
3. API endpoints
"""

import requests
import json
import asyncio

BASE_URL = "http://localhost:8000"

def test_endpoints():
    print("=" * 70)
    print("🧪 BACKEND API TEST SUITE")
    print("=" * 70)
    
    # 1. Test DB Health
    print("\n1️⃣  Testing /api/db-health...")
    try:
        resp = requests.get(f"{BASE_URL}/api/db-health", timeout=5)
        print(f"   Status: {resp.status_code}")
        data = resp.json()
        print(f"   Response: {json.dumps(data, indent=2)}")
        if resp.status_code == 200:
            print("   ✅ Database connected")
        else:
            print(f"   ❌ Database error: {data}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # 2. Test Bootstrap Cache
    print("\n2️⃣  Testing /api/bootstrap-cache (populate with fallback rates)...")
    try:
        resp = requests.get(f"{BASE_URL}/api/bootstrap-cache", timeout=5)
        print(f"   Status: {resp.status_code}")
        data = resp.json()
        print(f"   Response: {json.dumps(data, indent=2)}")
        if resp.status_code == 200:
            print("   ✅ Cache bootstrapped")
        else:
            print(f"   ❌ Bootstrap error: {data}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # 3. Test Live Rates
    print("\n3️⃣  Testing /api/live-rates...")
    try:
        resp = requests.get(f"{BASE_URL}/api/live-rates", timeout=5)
        print(f"   Status: {resp.status_code}")
        data = resp.json()
        print(f"   Rates: {json.dumps(data, indent=2)}")
        if resp.status_code == 200 and data.get("rates"):
            print(f"   ✅ Rates available: {len(data['rates'])} brands")
        else:
            print(f"   ⚠️  No rates or error: {data}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # 4. Test Categories
    print("\n4️⃣  Testing /api/categories...")
    try:
        resp = requests.get(f"{BASE_URL}/api/categories", timeout=5)
        print(f"   Status: {resp.status_code}")
        data = resp.json()
        if resp.status_code == 200:
            cats = data.get("categories", [])
            print(f"   ✅ Available categories: {len(cats)}")
            print(f"   First 5: {[c['label'] for c in cats[:5]]}")
        else:
            print(f"   ❌ Error: {data}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # 5. Test Brands
    print("\n5️⃣  Testing /api/brands...")
    try:
        resp = requests.get(f"{BASE_URL}/api/brands", timeout=5)
        print(f"   Status: {resp.status_code}")
        data = resp.json()
        if resp.status_code == 200:
            brands = data.get("brands", [])
            print(f"   ✅ Available brands: {brands}")
        else:
            print(f"   ❌ Error: {data}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # 6. Test Calculate Price
    print("\n6️⃣  Testing /api/calculate-price (22K Gold, 10g Earring)...")
    try:
        payload = {
            "weight": 10.0,
            "purity": "22K",
            "jewellery_type": "earring",
            "metal_type": "Gold"
        }
        resp = requests.post(
            f"{BASE_URL}/api/calculate-price",
            json=payload,
            timeout=10
        )
        print(f"   Status: {resp.status_code}")
        data = resp.json()
        
        if resp.status_code == 200:
            print(f"   ✅ Calculation successful")
            results = data.get("results", [])
            print(f"   Brands checked: {len(results)}")
            
            for result in results[:2]:  # Show first 2 brands
                brand = result.get("brand")
                total = result.get("total_estimated_price")
                rate = result.get("per_gram_rate")
                print(f"\n      {brand}:")
                print(f"         Rate: ₹{rate}/g")
                print(f"         Total (10g): ₹{total}")
        else:
            print(f"   ❌ Calculation error:")
            print(f"   {json.dumps(data, indent=2)}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # 7. Test Brand Summary
    print("\n7️⃣  Testing /api/brand-summary (Tanishq, 10g Earring, 22K)...")
    try:
        payload = {
            "brand": "Tanishq",
            "weight": 10.0,
            "purity": "22K",
            "category": "earring"
        }
        resp = requests.post(
            f"{BASE_URL}/api/brand-summary",
            json=payload,
            timeout=10
        )
        print(f"   Status: {resp.status_code}")
        data = resp.json()
        
        if resp.status_code == 200:
            items = data.get("total_items", 0)
            top_5 = data.get("top_5_deals", [])
            print(f"   ✅ Summary retrieved")
            print(f"   Total items found: {items}")
            print(f"   Top 5 deals: {len(top_5)}")
            
            if items > 0:
                print(f"\n      Searched range: {data.get('searched_range')}")
                if top_5:
                    print(f"      Best making charge: {top_5[0].get('mc')}%")
        else:
            print(f"   ⚠️  Error or no items:")
            print(f"   {json.dumps(data, indent=2)}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 70)
    print("✅ TEST SUITE COMPLETE")
    print("=" * 70)

if __name__ == "__main__":
    print("\n⏳ Waiting for backend to be ready...")
    print(f"   Target: {BASE_URL}")
    print("\n📌 Make sure backend is running:")
    print(f"   cd c:\\Users\\Asus\\Downloads\\pythonscrapper\\api")
    print(f"   python main.py")
    print("\n" + "-" * 70)
    
    input("\n   Press Enter when backend is running...")
    
    test_endpoints()
