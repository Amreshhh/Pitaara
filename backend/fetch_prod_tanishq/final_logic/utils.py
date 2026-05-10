from datetime import datetime
import re

def get_formatted_date():
    """Returns the current date in Malabar's format."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def detect_category(name_or_url):
    """Detects the jewelry category from the product name or URL."""
    if not name_or_url: 
        return "Other"
        
    lower_name = name_or_url.lower()
    
    if 'coin' in lower_name and 'pendant' in lower_name:
        return "Coin pendant"
    if ('drop' in lower_name or 'stud' in lower_name) and 'ring' in lower_name:
        return "Ring"
    # Updated Earring and Bali logic
    if 'watch' in lower_name and 'stud' in lower_name: return "Watch"
    if any(word in lower_name for word in ['earring', 'jhumka', 'jhumki','stud', 'drops','ear-cuffs','danglers', 'ear-cuff']): 
        return "Earring"
    if any(word in lower_name for word in ['bali']):
            return "Bali"
    if any (word in lower_name for word in ['hoops','hoop']): 
        return "Hoops"
    if any(word in lower_name for word in ['band']): 
        return "Band or Plain Ring"
    if 'ring' in lower_name: return "Ring"
    if 'choker' in lower_name: return "Choker"
    if 'sitahar' in lower_name: return "Sitahaar(a type of Necklace)"
    if any(word in lower_name for word in ['necklace', 'neckwear','neckalce']): return "Necklace"
    if 'chain' in lower_name: return "Chain"
    
    # Separated Bangles, Bracelet, and Kada
    if 'bangle' in lower_name: return "Bangle"
    if 'bracelet' in lower_name or 'braclet' in lower_name or 'barcelet' in lower_name or 'wristlet' in lower_name: return "Bracelet"
    if 'kada' in lower_name: return "Kada"
    
    if 'pendant' in lower_name: return "Pendant"
    if 'set' in lower_name: return "Set"
    if any(word in lower_name for word in ['mangalsutra', 'mangal sutra', 'mangal-sutra','mangalsuta']): return "Mangalsutra"
    
    # Separated Nose Pin and Nath
    if 'nose' in lower_name: return "Nose Pin"
    if 'nath' in lower_name: return "Nath"
    
    if any(word in lower_name for word in ['anklet', 'payal']): return "Anklet"

    if any(word in lower_name for word in ['maang tikka', 'maang', 'maang-tikka']): return "Maang Tikka"


    
# NEW LOGIC (Strict word checking)
    # \b ensures 'bar' only matches if it's surrounded by hyphens, slashes, etc.
    if 'coin' in lower_name or 'biscuit' in lower_name or re.search(r'\bbar\b', lower_name): 
        return "Coin"
    if 'watch' in lower_name: return "Watch"

    return "Other"

# ==========================================
# 🚀 MALABAR & SENCO LOGIC (Smart Classifier)
# ==========================================
def check_if_diamond(name_or_url, breakup_dict):
    text_lower = name_or_url.lower() if name_or_url else ""
    
    # Purity ko extract aur lowercase karna cross-check ke liye
    purity_lower = str(breakup_dict.get("purity", "Unknown")).lower()
    
    # 1. Keywords check karo
    has_solitaire_in_text = 'solitaire' in text_lower
    has_diamond_in_text = 'diamond' in text_lower or 'stone' in text_lower
    has_platinum_in_text = 'platinum' in text_lower
    has_silver_in_text = 'silver' in text_lower
    
    # 2. Charges check karo (🚀 TANISHQ WALA 2000 CAP LOGIC INTEGRATED)
    try:
        total_stone = float(breakup_dict.get('stone_charges', 0))
        # Agar stone charges 2000 se kam hain, toh use "Stone" category mein nahi dalenge
        if total_stone > 2000:
            has_stone_charges = True
        else:
            has_stone_charges = False
    except (ValueError, TypeError):
        has_stone_charges = False
        
    is_studded_diamond = has_diamond_in_text 
    is_studded_stone = has_stone_charges
    
    # Base Classification
    detailed_type = "Gold"
    
    if has_platinum_in_text:
        if is_studded_diamond:
            detailed_type = "Platinum & Diamond"
        elif is_studded_stone:
            detailed_type = "Platinum & Stone"
        elif has_solitaire_in_text:
            detailed_type = "Platinum Solitaire"
        else:
            detailed_type = "Platinum"
            
    elif is_studded_diamond:
        detailed_type = "Diamond"
    elif is_studded_stone:
        detailed_type = "Stone"
    elif has_solitaire_in_text:
        detailed_type = "Solitaire"
    elif has_silver_in_text:
        detailed_type = "Silver"


    # 3. 🚀 THE NEW PURITY CROSS-CHECKER
    
    # Case A: Naam mein/Type mein Gold aagaya, par purity mein Silver likha hai
    if 'silver' in purity_lower and 'gold' in detailed_type.lower():
        detailed_type = detailed_type.replace("Gold", "Silver")
        
    # Case B: Naam mein/Type mein Silver aagaya, par purity mein Gold likha hai (jaise 18K/22K)
    elif ('gold' in purity_lower or 'k' in purity_lower) and 'silver' in detailed_type.lower():
        # Specifically avoiding replacing if it's genuinely silver. But if purity says "18k Yellow Gold":
        if 'gold' in purity_lower:
            detailed_type = detailed_type.replace("Silver", "Gold")

    return detailed_type

# ==========================================
# 🚀 TANISHQ SPECIFIC LOGIC (Boolean Return)
# ==========================================
# ==========================================
# 🚀 TANISHQ SPECIFIC LOGIC (Detailed)
# ==========================================
def detect_tanishq_type(url, html_text, tree):
    """
    Tanishq scraper ke liye DOM aur keyword check. 
    Returns: (needs_api: bool, detailed_type: str)
    """
    html_text_upper = html_text.upper()
    url_lower = url.lower()
    
    # 1. Keywords Check
    has_solitaire = 'solitaire' in url_lower 
    has_diamond = 'diamond' in url_lower 
    has_stone = 'stone' in url_lower or 'gemstone' in url_lower 
    has_platinum = 'platinum' in url_lower 
    has_silver = 'silver' in url_lower 
    
    # 2. DOM Specific Blocks Check (Tanishq's specification table)
    if tree:
        spec_blocks = tree.css('.col-lg-4.col-6.mb-4')
        for block in spec_blocks:
            lbl = block.css_first('p')
            val = block.css_first('h4')
            if lbl and val and 'jewellery type' in lbl.text(strip=True).lower():
                v_text = val.text(strip=True).lower()
                if 'stone' in v_text or 'gemstone' in v_text: has_stone = True
                if 'diamond' in v_text: has_diamond = True
                if 'platinum' in v_text: has_platinum = True
                if 'silver' in v_text: has_silver = True
                if 'solitaire' in v_text: has_solitaire = True

    # 3. Determine Category String (Just like Malabar)
    detailed_type = "Gold"
    if has_platinum:
        if has_diamond: detailed_type = "Platinum & Diamond"
        elif has_stone: detailed_type = "Platinum & Stone"
        elif has_solitaire: detailed_type = "Platinum Solitaire"
        else: detailed_type = "Platinum"
    elif has_diamond:
        detailed_type = "Diamond"
    elif has_stone:
        detailed_type = "Stone"
    elif has_solitaire:
        detailed_type = "Solitaire"
    elif has_silver:
        detailed_type = "Silver"

    # 4. Routing Logic: Tanishq API hidden charges inke liye zaroori hai
    needs_api = has_diamond or has_stone or has_platinum or has_solitaire

    return needs_api, detailed_type

# utils.py ke end mein add karein
def refine_category_by_price(detailed_type, stone_charges_str):
    """
    Check karta hai ki stone charges 1000 se kam hain toh usko wapas Gold/Platinum me downgrade kar do.
    """
    if stone_charges_str == "N/A":
        stone_val = 0
    else:
        try:
            # "₹ 850.50" jaise text se number nikalna
            stone_val = float(re.sub(r'[^\d.]', '', stone_charges_str))
        except:
            stone_val = 0

    # 1000 Rs ka Cap Logic
    if stone_val <= 2000:
        if detailed_type == "Stone":
            return "Gold"
        elif detailed_type == "Platinum & Stone":
            return "Platinum"
            
    return detailed_type

def infer_missing_purity(item_dict, live_rates_cache):
    """
    Checks if purity is missing. If so, calculates the implied gold rate
    and matches it to the closest live rate to infer the purity.
    
    live_rates_cache should look like: {'24K': 7500, '22K': 6875, '18K': 5625, '14K': 4375}
    """
    # 1. Check if purity is actually missing
    current_purity = str(item_dict.get("purity", "Not Found")).strip()
    
    if current_purity.upper() not in ["NOT FOUND", "", "NULL", "NONE"]:
        return current_purity # Purity already exists, return it as-is
        
    # 2. Extract values safely
    try:
        # Replace these keys with the exact keys your JSON/Dictionary uses
        gold_value = float(item_dict.get("gold_value", 0)) 
        net_weight = float(item_dict.get("net_weight", 0))
        
        # Prevent division by zero
        if net_weight <= 0 or gold_value <= 0:
            return "Not Found"
            
        # 3. Calculate the implied rate
        implied_rate = gold_value / net_weight
        
        # 4. Find the closest match in your live rates
        # This finds the key (e.g., '22K') where the difference between the live rate and implied rate is the smallest
        closest_purity = min(
            live_rates_cache.keys(), 
            key=lambda k: abs(live_rates_cache[k] - implied_rate)
        )
        
        # 5. Add a safety threshold (e.g., Max tolerance of ₹300/gram difference)
        # If the closest rate is still way off, it's safer to keep it as "Not Found"
        difference = abs(live_rates_cache[closest_purity] - implied_rate)
        
        if difference <= 300: 
            return closest_purity
        else:
            return "Not Found"
            
    except (ValueError, TypeError):
        # If strings are passed instead of numbers and can't be converted
        return "Not Found"

# ==========================================
# 🚀 TANISHQ PURITY NORMALIZATION LOGIC
# ==========================================
def normalize_purity(purity_value):
    """
    Converts numeric/decimal purity values to standard K format.
    Examples: "99.9" → "24K", "91.6" → "22K", "75" → "18K", "58.3" → "14K"
    
    Also handles: "22K", "22k", "22 K" → standardized to "22K"
    """
    if not purity_value or purity_value == "Not Found":
        return "Not Found"
    
    purity_str = str(purity_value).strip().upper()
    
    # Already in K format (e.g., "22K", "22k")
    if 'K' in purity_str:
        # Standardize: "22k" or "22 K" → "22K"
        match = re.search(r'(\d+)\s*K', purity_str)
        if match:
            karat = match.group(1)
            return f"{karat}K"
        return purity_str
    
    # Convert numeric purity to K format
    try:
        purity_num = float(purity_str)
        
        # Purity range detection (with tolerance)
        if 99 <= purity_num <= 100: return "24K"
        elif 90 <= purity_num < 99: return "22K"
        elif 74 <= purity_num < 90: return "18K"
        elif 58 <= purity_num < 74: return "14K"
        else:
            return purity_str  # Keep original if doesn't match any standard
    except (ValueError, TypeError):
        # If can't convert to float, keep original
        return purity_str

def extract_purity_from_url(url):
    """
    Attempts to extract purity from Tanishq URL if present.
    Example: ...naaaa00.html → looks for 24K/22K/18K/14K patterns in URL
    Returns: "24K", "22K", "18K", "14K" or "Not Found"
    """
    if not url:
        return "Not Found"
    
    url_lower = url.lower()
    
    # Look for explicit K patterns in URL (e.g., "22k", "18kt")
    purity_patterns = [
        (r'24k', "24K"),
        (r'22k', "22K"),
        (r'18k', "18K"),
        (r'14k', "14K"),
    ]
    
    for pattern, karat in purity_patterns:
        if re.search(pattern, url_lower):
            return karat
    
    return "Not Found"

def override_purity_with_url(extracted_purity, url):
    """
    Smart purity override logic:
    1. If URL has explicit purity → use URL purity
    2. If extracted purity matches URL purity → keep extracted
    3. If mismatch and URL has purity → override with URL purity
    4. If no URL purity → keep extracted (after normalization)
    
    Returns: final_purity after all checks
    """
    # Normalize the extracted purity first
    normalized_extracted = normalize_purity(extracted_purity)
    
    # Try to extract purity from URL
    url_purity = extract_purity_from_url(url)
    
    # If URL has no explicit purity, return normalized extracted
    if url_purity == "Not Found":
        return normalized_extracted
    
    # If extracted purity is "Not Found", use URL purity
    if normalized_extracted == "Not Found":
        return url_purity
    
    # Both have values - if they match, keep extracted; if not, use URL
    if normalized_extracted == url_purity:
        return normalized_extracted
    else:
        # Mismatch detected - prefer URL purity as it's from product slug
        return url_purity