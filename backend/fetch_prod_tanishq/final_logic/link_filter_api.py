import re
import os
import sys
from selectolax.parser import HTMLParser
from datetime import datetime

# ==========================================
# 🚀 UTILS INTEGRATION (Bulletproof Logic)
# ==========================================
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
root_path = os.path.dirname(parent_dir)

if root_path not in sys.path:
    sys.path.append(root_path)

from utils import refine_category_by_price, infer_missing_purity


async def extract_via_api(url, tree, pid, session, detailed_type="Stone/Diamond (API Hit)", live_rates_cache=None):
    """
    Yeh function DOM se Weight/Purity nikalega, 
    aur API hit karke Making, Stone, aur 'Gold Final Value' nikalega.
    
    🚀 NAYA: live_rates_cache parameter added for purity inference
    Expected format: {'24K': 7500, '22K': 6875, '18K': 5625, '14K': 4375}
    """
    # ==============================================================
    # STEP 1: FRONTEND SE BASIC DETAILS NIKALNA
    # ==============================================================
    price = "Not Found"
    weight = "Not Found"
    purity = "Not Found"
    brand_name = "Tanishq (Rupees)" # Defaulting to Rupees

    price_element = tree.css_first('.pdp-product-main-sale-price')
    if price_element:
        raw_price = price_element.text(strip=True)
        
        # 🚀 NAYA: Currency Checker Logic
        if '$' in raw_price or 'USD' in raw_price.upper():
            brand_name = "Tanishq (Dollars)"
        elif '₹' in raw_price or 'INR' in raw_price.upper() or 'RS' in raw_price.upper():
            brand_name = "Tanishq (Rupees)"

        clean_price = re.sub(r'[^\d]', '', raw_price)
        if clean_price:
            price = int(clean_price)

    spec_blocks = tree.css('.col-lg-4.col-6.mb-4')
    for block in spec_blocks:
        label_el = block.css_first('p')
        value_el = block.css_first('h4')
        
        if label_el and value_el:
            label_text = label_el.text(strip=True).lower()
            value_text = value_el.text(strip=True)
            
            if 'weight' in label_text:
                weight_match = re.search(r'([\d.]+)', value_text)
                if weight_match:
                    weight = float(weight_match.group(1))
            elif 'karatage' in label_text:
                purity = value_text 

    # ==============================================================
    # STEP 2: API HIT KARKE HIDDEN CHARGES NIKALNA
    # ==============================================================
    making_charges = "N/A"
    stone_charges = "N/A"
    gold_value_str = "N/A"
    grand_total = "N/A"

    if pid:
        api_url = f"https://www.tanishq.co.in/on/demandware.store/Sites-Tanishq-Site/en_IN/Product-PriceBreakup?pid={pid}"
        try:
            api_res = await session.get(api_url, headers={'X-Requested-With': 'XMLHttpRequest'}, timeout=30)
            api_tree = HTMLParser(api_res.text)

            rows = api_tree.css('.col-values, div.row, tr')
            
            for row in rows:
                text = row.text(separator=' ', strip=True).lower()
                
                if "gold" in text and "final value" in text:
                    items = row.css('.indivi-item')
                    for item in items:
                        if 'final value' in item.text(strip=True).lower():
                            val_span = item.css_first('span')
                            if val_span: gold_value_str = val_span.text(strip=True)
                            break
                            
                    if gold_value_str == "N/A":
                        rgt = row.css_first('.float-right, .mob-rgt-cls')
                        if rgt and ('₹' in rgt.text(strip=True) or '$' in rgt.text(strip=True)):
                            gold_value_str = rgt.text(strip=True)

                elif ("stone" in text or "diamond" in text) and "final value" in text:
                    items = row.css('.indivi-item')
                    for item in items:
                        if 'final value' in item.text(strip=True).lower():
                            val_span = item.css_first('span')
                            if val_span: stone_charges = val_span.text(strip=True)
                            break
                    if stone_charges == "N/A":
                        rgt = row.css_first('.float-right, .mob-rgt-cls')
                        if rgt and ('₹' in rgt.text(strip=True) or '$' in rgt.text(strip=True)): stone_charges = rgt.text(strip=True)

                elif "making charges" in text:
                    items = row.css('.indivi-item')
                    for item in items:
                        if 'making charges' in item.text(strip=True).lower():
                            val_span = item.css_first('span')
                            if val_span: making_charges = val_span.text(strip=True)
                            break
                    if making_charges == "N/A":
                        rgt = row.css_first('.float-right, .mob-rgt-cls, .value, td:last-child')
                        if rgt: making_charges = rgt.text(strip=True)

                elif "grand total" in text:
                    items = row.css('.indivi-item')
                    for item in items:
                        if 'grand total' in item.text(strip=True).lower():
                            val_span = item.css_first('span')
                            if val_span: grand_total = val_span.text(strip=True)
                            break
                    if grand_total == "N/A":
                        rgt = row.css_first('.float-right, .mob-rgt-cls, .value, td:last-child')
                        if rgt: grand_total = rgt.text(strip=True)

            if grand_total == "N/A":
                grand_node = api_tree.css_first('.mobile-grand-total .mob-rgt-cls, .grand-total-values .mob-rgt-cls')
                if grand_node: grand_total = grand_node.text(strip=True)

        except Exception as e:
            print(f"⚠️ API Error on {pid}: {e}")

    # ==============================================================
    # STEP 3: PERCENTAGE CALCULATION
    # ==============================================================
    mc_percentage = "N/A"
    
    if making_charges != "N/A" and gold_value_str != "N/A":
        try:
            mc_num = float(re.sub(r'[^\d.]', '', making_charges))
            gv_num = float(re.sub(r'[^\d.]', '', gold_value_str))
            
            if gv_num > 0:
                mc_percent_val = round((mc_num / gv_num) * 100, 2)
                mc_percentage = f"{mc_percent_val} %"
        except Exception as e:
            pass

        final_detailed_type = refine_category_by_price(detailed_type, stone_charges)

    # ==============================================================
    # 🚀 STEP 4: PURITY INFERENCE (NEW)
    # ==============================================================
    # Agar purity "Not Found" hai aur live_rates_cache available hai, 
    # toh gold_value aur weight use karke infer karna
    inferred_purity = purity
    if purity == "Not Found" and live_rates_cache and gold_value_str != "N/A" and weight != "Not Found":
        try:
            # Extract numeric gold value
            gold_val_numeric = float(re.sub(r'[^\d.]', '', gold_value_str))
            
            # Create item dict for inference
            item_for_inference = {
                "gold_value": gold_val_numeric,
                "net_weight": weight  # Using gross weight as approximation
            }
            
            inferred_purity = infer_missing_purity(item_for_inference, live_rates_cache)
        except Exception as e:
            # Agar inference fail ho toh original purity rakhna
            pass

    return {
        "Brand": brand_name,  # 🚀 Updated Dynamically
        "product_url": url,
        "sku": pid,
        "type": final_detailed_type,   
        "purity": inferred_purity,  # 🚀 Now can be inferred
        "net_weight": weight if weight != "Not Found" else weight,
        "making_charges_percentage": mc_percentage,
        "extraction_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }