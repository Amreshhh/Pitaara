import json
from selectolax.parser import HTMLParser

def extract_senco_breakup_python(html_content):
    default_breakup = {
        "purity": "Unknown",
        "gross_weight": 0.0,
        "making_charges_percentage": "0 %",
        "stone_charges": 0.0
    }

    try:
        if "cloudflare" in html_content.lower() or "just a moment" in html_content.lower():
            print("🛑 [BLOCKED] Cloudflare ne pakad liya! Request slow karni padegi.")
            return default_breakup

        tree = HTMLParser(html_content)
        next_data_node = tree.css_first('#__NEXT_DATA__')
        
        if not next_data_node:
            return default_breakup

        json_data = json.loads(next_data_node.text())
        product_data = json_data.get("props", {}).get("pageProps", {}).get("initialState", {}).get("product", {})
        
        # Sometime details are directly in product, sometimes in selectedPrice
        selected_price = product_data.get("selectedPrice", {}) or product_data
        discount_dict = selected_price.get("discount", {}) or {}

        # 🚀 HELPER FUNCTION: Ye sabse reliable tarika hai multiple keys check karne ka
        def safe_get(dicts_list, keys_list):
            for d in dicts_list:
                if not isinstance(d, dict): continue
                for k in keys_list:
                    val = d.get(k)
                    if val is not None and str(val).strip() != "":
                        try:
                            return float(val)
                        except ValueError:
                            pass
            return 0.0

        # Dono dictionaries me ye saari possible keys check karega
        sources = [discount_dict, selected_price, product_data]

        # 1. Gold Value (Senco ke sab possible naam)
        gold_keys = ["gold_value", "metal_value", "gold_price", "metal_price"]
        gold_value = safe_get(sources, gold_keys)

        # 2. Making Charges (Saari possible keys)
        mc_keys = ["making_charge", "making_charge_value", "making_charges"]
        making_charges = safe_get(sources, mc_keys)

        # 3. Stone/Diamond Charges
        dia_val = safe_get(sources, ["diamond_value", "diamond_value_inr", "diamond_charge"])
        stone_val = safe_get(sources, ["stone_value", "stone_value_inr", "stone_charge"])
        total_stone_charges = dia_val + stone_val

        # 4. Math for Making Charge Percentage
        mc_percentage_str = "N/A"
        if gold_value > 0:
            mc_pct = (making_charges / gold_value) * 100
            mc_percentage_str = f"{round(mc_pct, 2)} %"
            
        # 5. Basic Info
        purity = selected_price.get("purity") or selected_price.get("gold_purity_display_name") or product_data.get("gold_purity_display_name") or "Unknown"
        gross_weight = safe_get(sources, ["gross_weight", "gold_weight", "metal_weight", "weight"])

        return {
            "purity": purity,
            "gross_weight": gross_weight,
            "making_charges_percentage": mc_percentage_str,
            "stone_charges": total_stone_charges
        }

    except Exception as e:
        print(f"\n⚠️ [CRASH] Extractor fail hua: {e}")
        return default_breakup