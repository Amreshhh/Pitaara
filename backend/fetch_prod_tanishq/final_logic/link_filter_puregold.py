import re
# 🚀 NAYA: Calculator import kar liya
from calculator import calculate_making_charges_percentage
from datetime import datetime

def extract_basic_details(url, tree, pid="N/A", detailed_type="Pure Gold"):   
    """
    Yeh function sirf DOM Tree lega aur bina network call ke
    Price, Weight, aur Purity extract karega.
    Uske baad calculator.py ko call karke Making Charge % nikalega.
    """
    price = "Not Found"
    weight = "Not Found"
    purity = "Not Found"
    brand_name = "Tanishq (Rupees)" # Defaulting to Rupees

    # --- Extract Price (Selectolax Logic) ---
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

    # --- Extract Specifications (Selectolax Logic) ---
    spec_blocks = tree.css('.col-lg-4.col-6.mb-4')
    for block in spec_blocks:
        label_el = block.css_first('p')
        value_el = block.css_first('h4')
        
        if label_el and value_el:
            label_text = label_el.text(strip=True).lower()
            value_text = value_el.text(strip=True)
            
            if 'net weight' in label_text:
                weight_match = re.search(r'([\d.]+)', value_text)
                if weight_match:
                    weight = float(weight_match.group(1))
            elif 'karatage' in label_text:
                purity = value_text 

    # ==============================================================
    # 🚀 NAYA: CALCULATOR INTEGRATION
    # ==============================================================
    mc_rs = "N/A"
    mc_percent = "N/A"

    if price != "Not Found" and weight != "Not Found":
        try:
            calc_result = calculate_making_charges_percentage(price, weight, purity)
            mc_rs = f"₹ {calc_result['making_charge_rs']}"
            mc_percent = f"{calc_result['making_charges_percentage']} %"
        except Exception as e:
            print(f"⚠️ Calculator error on {pid}: {e}")
            
    return {
        "Brand": brand_name, # 🚀 Updated Dynamically
        "product_url": url,
        "sku": pid,
        "type": detailed_type,
        "purity": purity,
        "net_weight": weight,
        "making_charges_percentage": mc_percent,
        "extraction_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }