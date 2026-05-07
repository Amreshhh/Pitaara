import json
from selectolax.parser import HTMLParser

# 🚀 NAYA: Parameter mein 'product_title' bhi add kar diya
def extract_senco_breakup_python(html_content, product_url="Unknown", product_title="Unknown"):
    default_breakup = {
        "purity": "Unknown",
        "gross_weight": 0.0,
        "making_charges_percentage": "0 %",
        "stone_charges": 0.0
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

        gold_value = safe_get(sources, ["gold_value", "metal_value", "gold_price", "metal_price"])
        making_charges = safe_get(sources, ["making_charge", "making_charge_value", "making_charges"])
        
        dia_val = safe_get(sources, ["diamond_value", "diamond_value_inr", "diamond_charge"])
        stone_val = safe_get(sources, ["stone_value", "stone_value_inr", "stone_charge"])
        total_stone_charges = dia_val + stone_val

        # ==========================================
        # 🚀 QUICK TYPE CHECK FOR LOGGING (PLATINUM INTEGRATED)
        # ==========================================
        text_lower = product_title.lower()
        
        has_solitaire = 'solitaire' in text_lower
        is_studded = 'diamond' in text_lower or 'stone' in text_lower or total_stone_charges > 0
        has_platinum = 'platinum' in text_lower

        if has_platinum:
            if is_studded:
                log_type = "Platinum Stone/Diamond"
            elif has_solitaire:
                log_type = "Platinum Solitaire"
            else:
                log_type = "Platinum"
        else:
            if is_studded:
                log_type = "Stone/Diamond"
            elif has_solitaire:
                log_type = "Solitaire"
            else:
                log_type = "Gold"

        # 🚀 Yahan Gold Value ke theek baad Type print ho raha hai
        log_text = f"URL: {product_url}\nGold Value: {gold_value} | Type: {log_type} | Making Charges: {making_charges}\n{'-'*60}\n"
        
        with open("senco_debug_log.txt", "a", encoding="utf-8") as log_file:
            log_file.write(log_text)
        # ==========================================

        mc_percentage_str = "N/A"
        if gold_value > 0:
            mc_pct = (making_charges / gold_value) * 100
            mc_percentage_str = f"{round(mc_pct, 2)} %"
            
        purity = selected_price.get("purity") or selected_price.get("gold_purity_display_name") or product_data.get("gold_purity_display_name") or "Unknown"
        gross_weight = safe_get(sources, ["gross_weight", "gold_weight", "metal_weight", "weight"])

        return {
            "purity": purity,
            "gross_weight": gross_weight,
            "making_charges_percentage": mc_percentage_str,
            "stone_charges": total_stone_charges
        }

    except Exception as e:
        with open("senco_debug_log.txt", "a", encoding="utf-8") as log_file:
            log_file.write(f"⚠️ CRASH for URL: {product_url} | Error: {e}\n{'-'*60}\n")
        return default_breakup