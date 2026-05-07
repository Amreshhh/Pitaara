import json
from selectolax.parser import HTMLParser

def extract_senco_breakup_python(html_content, product_url="Unknown", product_title="Unknown"):
    default_breakup = {
        "purity": "Unknown",
        "net_weight": 0.0,       # 🚀 Naya addition
        "gross_weight": 0.0,
        "making_charges_percentage": "0 %",
        "stone_charges": 0.0,
        "platinum_weight": 0.0,
        "platinum_purity": "Unknown"
    }

    try:
        if "cloudflare" in html_content.lower() or "just a moment" in html_content.lower():
            return default_breakup

        tree = HTMLParser(html_content)
        next_data_node = tree.css_first('#__NEXT_DATA__')
        
        if not next_data_node:
            return default_breakup

        json_data = json.loads(next_data_node.text())
        product_data = json_data.get("props", {}).get("pageProps", {}).get("initialState", {}).get("product", {})
        
        selected_price = product_data.get("selectedPrice", {}) or product_data
        discount_dict = selected_price.get("discount", {}) or {}

        def safe_get(dicts_list, keys_list):
            for d in dicts_list:
                if not isinstance(d, dict): continue
                for k in keys_list:
                    val = d.get(k)
                    if val is not None and str(val).strip() != "":
                        try: return float(val)
                        except ValueError: pass
            return 0.0

        sources = [discount_dict, selected_price, product_data]

        # ==========================================
        # 🚀 THE NEW WEIGHT LOGIC
        # ==========================================
        # Extract explicitly based on key names
        raw_gross = safe_get(sources, ["gross_weight", "total_weight", "weight"])
        raw_net = safe_get(sources, ["net_weight", "metal_weight", "gold_weight", "stone_less_weight"])

        # Fallback: Agar stone nahi hai, toh Gross aur Net same hoga
        if raw_net == 0.0 and raw_gross > 0.0:
            raw_net = raw_gross
        elif raw_gross == 0.0 and raw_net > 0.0:
            raw_gross = raw_net

      # ... (sources = [discount_dict, selected_price, product_data] wali line ke baad) ...

        # ==========================================
        # 🚀 STANDARD GOLD & MAKING CHARGES (THE FIX)
        # ==========================================
        # Rupaye (INR) wali fields ko strict priority deni hai taaki percentage extract na ho jaye
        gold_value = safe_get(sources, ["metal_value", "gold_value", "total_metal_value", "gold_price", "metal_price"])
        making_charges_inr = safe_get(sources, ["making_charge_value", "making_charge_inr", "total_making_charge"])
        
        # Agar Senco direct 30% likh kar bhej raha hai (Fallback ke liye)
        direct_mc_percent = safe_get(sources, ["making_charge", "making_charge_percentage", "making_charge_percent"])

        dia_val = safe_get(sources, ["diamond_value", "diamond_value_inr", "diamond_charge"])
        stone_val = safe_get(sources, ["stone_value", "stone_value_inr", "stone_charge"])
        total_stone_charges = dia_val + stone_val

        # Fetching Platinum Details & Value
        plat_weight = safe_get(sources, ["platinum_weight"])
        plat_value = safe_get(sources, ["platinum_value", "platinum_value_inr", "platinum_price"]) 
        
        plat_purity_raw = selected_price.get("platinum_purity") or product_data.get("platinum_purity")
        plat_purity = str(plat_purity_raw).strip() if plat_purity_raw else "Unknown"

        # ==========================================
        # 🚀 THE SMART MATH (PLATINUM VS GOLD)
        # ==========================================
        is_platinum = "platinum" in product_title.lower()
        base_metal_value = plat_value if is_platinum else gold_value

        mc_percentage_str = "N/A"
        
        # 🔥 THE EXACT FORMULA: (Making Charge INR / Gold Value) * 100
        if base_metal_value > 0 and making_charges_inr > 0:
            mc_pct = (making_charges_inr / base_metal_value) * 100
            mc_percentage_str = f"{round(mc_pct, 2)} %"
            
        # Agar INR 0 hai par direct percentage value maujood hai
        elif direct_mc_percent > 0:
            mc_percentage_str = f"{round(direct_mc_percent, 2)} %"
            
        elif gold_value == 0 and plat_value == 0:
            pass # Silent ignore to keep terminal clean

        purity = selected_price.get("purity") or selected_price.get("gold_purity_display_name") or product_data.get("gold_purity_display_name") or "Unknown"

        return {
            "purity": purity,
            "net_weight": raw_net,       
            "gross_weight": raw_gross,   
            "making_charges_percentage": mc_percentage_str,
            "stone_charges": total_stone_charges,
            "platinum_weight": plat_weight,
            "platinum_purity": plat_purity
        }

    except Exception:
        return default_breakup