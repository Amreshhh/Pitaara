#!/usr/bin/env python3
"""Analyze inventory_malabar.json to find categories with 0-1g products."""

import json
from collections import defaultdict
from pathlib import Path

def analyze_inventory():
    inventory_file = Path(__file__).parent.parent / "api" / "inventory_malabar.json"
    
    with open(inventory_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Extract all items from nested structure
    all_items = []
    for brand_data in data:
        if isinstance(brand_data, dict):
            for brand, items in brand_data.items():
                if isinstance(items, list):
                    all_items.extend(items)
    
    # Analyze 0-1g range products
    zero_to_one_categories = defaultdict(lambda: {'brands': set(), 'purities': set(), 'total_products': 0})
    all_categories = set()
    all_weight_ranges = defaultdict(set)
    
    for item in all_items:
        if not isinstance(item, dict):
            continue
        
        category = item.get('category', '')
        brand = item.get('Brand', '')
        purity = item.get('purity', '')
        label = item.get('label', '')
        product_count = item.get('product_count', 0)
        
        all_categories.add(category)
        all_weight_ranges[category].add(label)
        
        if label == '0g - 1g':
            zero_to_one_categories[category]['brands'].add(brand)
            zero_to_one_categories[category]['purities'].add(purity)
            zero_to_one_categories[category]['total_products'] += product_count
    
    # Print analysis
    print("=" * 80)
    print("CATEGORIES WITH PRODUCTS IN 0-1g RANGE")
    print("=" * 80)
    print()
    
    for category in sorted(zero_to_one_categories.keys()):
        data = zero_to_one_categories[category]
        print(f"📦 {category}")
        print(f"   Brands: {', '.join(sorted(data['brands']))}")
        print(f"   Purities: {', '.join(sorted(data['purities']))}")
        print(f"   Total Products: {data['total_products']}")
        print()
    
    print("=" * 80)
    print("CATEGORIES WITHOUT PRODUCTS IN 0-1g RANGE")
    print("=" * 80)
    print()
    
    categories_without_0_1g = all_categories - set(zero_to_one_categories.keys())
    for category in sorted(categories_without_0_1g):
        if category:  # Skip empty categories
            ranges = sorted(all_weight_ranges[category], key=lambda x: float(x.split('g')[0].split(' - ')[0].strip()) if ' - ' in x else 0)
            print(f"📦 {category}")
            print(f"   Available ranges: {', '.join(ranges[:5])}{'...' if len(ranges) > 5 else ''}")
            print()
    
    # Summary statistics
    print("=" * 80)
    print("SUMMARY STATISTICS")
    print("=" * 80)
    print(f"Total categories: {len(all_categories)}")
    print(f"Categories with 0-1g products: {len(zero_to_one_categories)}")
    print(f"Categories without 0-1g products: {len(categories_without_0_1g)}")
    print()
    
    # Total products in 0-1g range
    total_0_1g_products = sum(data['total_products'] for data in zero_to_one_categories.values())
    print(f"Total products in 0-1g range across all brands: {total_0_1g_products}")

if __name__ == "__main__":
    analyze_inventory()
