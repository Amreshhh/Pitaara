import json

def find_duplicates(filepath, unique_key=None):
    """
    JSON file mein duplicates dhoondhta hai.
    :param filepath: Aapki JSON file ka path
    :param unique_key: (Optional) Agar kisi specific key (jaise 'sku') se check karna ho.
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"❌ Error: File '{filepath}' nahi mili.")
        return
    except json.JSONDecodeError:
        print(f"❌ Error: File '{filepath}' valid JSON nahi hai.")
        return

    if not isinstance(data, list):
        print("⚠️ Warning: Ye file List format [{}, {}] mein nahi hai. Ye script list of dictionaries pe kaam karti hai.")
        return

    duplicates = []
    seen = set()

    if unique_key:
        print(f"🔍 Checking for duplicates based on key: '{unique_key}'...")
        for item in data:
            if isinstance(item, dict) and unique_key in item:
                val = item[unique_key]
                if val in seen:
                    duplicates.append(item)
                else:
                    seen.add(val)
    else:
        print("🔍 Checking for EXACT item duplicates...")
        for item in data:
            # Dictionary ko compare karne ke liye string format mein badalna padta hai
            serialized_item = json.dumps(item, sort_keys=True)
            if serialized_item in seen:
                duplicates.append(item)
            else:
                seen.add(serialized_item)

    # 📊 Results Display
    if duplicates:
        print(f"\n⚠️ Total {len(duplicates)} duplicates found out of {len(data)} items!")
        print("Pehle 3 duplicates ka sample:")
        for dup in duplicates[:3]:
            print(json.dumps(dup, indent=2))
        if len(duplicates) > 3:
            print(f"... aur {len(duplicates) - 3} aur duplicates hain.")
    else:
        print(f"\n✅ Koi duplicate nahi mila! File ekdum saaf hai ({len(data)} items).")

    return duplicates


# ==========================================
# 🚀 KAISE USE KAREIN:
# ==========================================
if __name__ == "__main__":
    file_name = "malabar_all_19k_links.json" # Yahan apni file ka naam daalo
    
    # CASE 1: Agar kisi specific key (jaise 'sku') ke hisaab se dhoondhna hai (Best for your scrapers)
    # duplicate_items = find_duplicates(file_name, unique_key='sku')

    # CASE 2: Agar EXACT pura ka pura entry duplicate dhoondhna hai
    duplicate_items = find_duplicates(file_name)