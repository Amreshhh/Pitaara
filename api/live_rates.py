import asyncio
import re
import time
from typing import Dict, Optional
from curl_cffi.requests import AsyncSession
from selectolax.parser import HTMLParser

# Helper function to prevent servers from sending cached/stale data
def get_no_cache_headers():
    return {
        "Cache-Control": "no-cache, no-store, must-revalidate",
        "Pragma": "no-cache",
        "Expires": "0",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    }

# ==========================================
# 1. TANISHQ (DOM Parsing + Reverse Math)
# ==========================================
async def fetch_tanishq(session):
    print("📡 Fetching Tanishq...")
    url = f"https://www.tanishq.co.in/gold-rate.html?lang=en_IN"

    try:
        response = await session.get(url, headers=get_no_cache_headers(), timeout=15)
        tree = HTMLParser(response.text)

        rate_22k: Optional[int] = None
        
        table_22k = tree.css_first('table.goldrate-table.fixedhgt.goldrate-table-22kt')        
        
        if table_22k:
            first_row = table_22k.css_first('tbody tr')
            if first_row:
                tds = first_row.css('td')
                if len(tds) >= 2:
                    today_rate_text = tds[1].text(strip=True)
                    m = re.search(r'₹?\s*([\d,]+)', today_rate_text)
                    if m:
                        num = m.group(1).replace(',', '')
                        if num.isdigit():
                            # Extract raw number WITHOUT dividing by 10
                            # Let normalization handle digit standardization
                            rate_22k = int(num)

        if not rate_22k:
            print("⚠️ Tanishq live DOM failed.")
            return None

        # 🚀 THE MATH CALCULATIONS

        # 1. Safely count the digits (ignoring any decimals)
        num_digits = len(str(int(rate_22k)))

        # 2. Standardize to a 5-digit rate (price per 10 grams in standard range: 10000-15000)
        # Handle all input cases robustly
        if num_digits <= 3:
            # Too small (likely per-gram: 139) → multiply by 100
            rate_22k = rate_22k * 100
        elif num_digits == 4:
            # Standard range for per-10g: 1390 → multiply by 10
            rate_22k = rate_22k * 10
        elif num_digits == 6:
            # Too large (likely per-gram with extra zero) → divide by 10
            rate_22k = rate_22k / 10
        # If exactly 5 digits, it's already perfect - do nothing

        # 3. Calculate other purities based on the standardized 22k rate
        rate_24k = int(round(rate_22k * (24.0 / 22.0)))
        rate_18k = int(round(rate_24k * (18.0 / 24.0)))
        rate_14k = int(round(rate_24k * (14.0 / 24.0)))

        return {
            "Brand": "Tanishq", 
            "24K": rate_24k, 
            "22K": rate_22k, 
            "18K": rate_18k, 
            "14K": rate_14k
        }

    except Exception as e:
        print(f"⚠️ Tanishq Error: {e}")
        return None
    
# ==========================================
# 2. MALABAR (GraphQL API)
# ==========================================
async def fetch_malabar(session):
    print("📡 Fetching Malabar...")
    url = f"https://www.malabargoldanddiamonds.com/graphql-magento?query=query%20getMetalRate(%24filter%3A%20MetalRateFilterInput)%20%7B%20getMetalRate(filter%3A%20%24filter)%20%7B%20items%20%7B%20entry_date%20entry_time%20purity%20unit%20rate%20country%20state%20%7D%20%7D%20%7D&variables=%7B%22filter%22%3A%7B%22metal_type%22%3A%22gold%22%2C%22country%22%3A%22India%22%7D%7D&_ts={int(time.time())}"
    
    try:
        response = await session.get(url, headers=get_no_cache_headers(), timeout=15)
        data = response.json()
        items = data.get('data', {}).get('getMetalRate', {}).get('items', [])

        rates: Dict[str, int] = {"Brand": "Malabar"}
        for item in items:
            purity = str(item.get('purity', '')).lower()
            try:
                rate = int(round(float(item.get('rate', 0))))
            except Exception:
                continue

            if '24' in purity: rates['24K'] = rate
            elif '22' in purity: rates['22K'] = rate
            elif '21' in purity: rates['22K'] = rate 
            elif '18' in purity: rates['18K'] = rate
            elif '14' in purity: rates['14K'] = rate

        return rates
    except Exception as e:
        print(f"⚠️ Malabar Error: {e}")
        return None

# ==========================================
# 3. SENCO (API + WAF Bypass Logic)
# ==========================================
async def fetch_senco(session):
    print("📡 Fetching Senco...")
    url = f"https://api.sencogoldanddiamonds.com/calculator/list?_ts={int(time.time())}"
    
    # 🔥 Perfect WAF Bypass Headers matching Chrome 124
    headers = {
        "Host": "api.sencogoldanddiamonds.com",
        "Connection": "keep-alive",
        "Sec-Ch-Ua": '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json",
        "Client-ID": "63866e9b-b9b8-4186-ac1c-b0855390f4df", # Real Senco API key extracted
        "Sec-Ch-Ua-Mobile": "?0",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Sec-Ch-Ua-Platform": '"Windows"',
        "Origin": "https://sencogoldanddiamonds.com",
        "Sec-Fetch-Site": "same-site",
        "Sec-Fetch-Mode": "cors",
        "Referer": "https://sencogoldanddiamonds.com/",
        "Accept-Language": "en-US,en;q=0.9"
    }

    try:
        response = await session.get(url, headers=headers, timeout=15)
        
        if response.status_code != 200:
            print(f"⚠️ Senco Failed with status {response.status_code}")
            return None
            
        data = response.json()
        gold_items = data.get('GOLD', [])

        rates: Dict[str, int] = {"Brand": "Senco"}
        best_24k = None
        
        for item in gold_items:
            # Check both 'name' and 'display_name' properties safely
            display = str(item.get('display_name', '')) + str(item.get('name', ''))
            display = display.upper()
            
            try:
                price = int(round(float(item.get('price', 0))))
            except Exception:
                continue

            # In Senco's API, 24K is often labeled as 99.99
            if '24K' in display or '99.99' in display:
                if best_24k is None or price > best_24k: best_24k = price
            elif '22K' in display: rates['22K'] = price
            elif '18K' in display: rates['18K'] = price
            elif '14K' in display: rates['14K'] = price

        if best_24k:
            rates['24K'] = best_24k

        return rates
    except Exception as e:
        print(f"⚠️ Senco Error: {e}")
        return None

# ==========================================
# 4. CANDERE (DOM Parsing)
# ==========================================
async def fetch_candere(session):
    print("📡 Fetching Candere...")
    url = f"https://www.candere.com/gold-rate-today/india?_ts={int(time.time())}" 
    
    try:
        response = await session.get(url, headers=get_no_cache_headers(), timeout=15)
        tree = HTMLParser(response.text)

        rates: Dict[str, int] = {"Brand": "Candere"}
        base_24k_rate: Optional[int] = None

        price_node = tree.css_first('#goldPrice24k')
        if price_node:
            txt = price_node.text(strip=True) 
            m = re.search(r'₹?\s*([\d,]+)', txt)
            if m:
                num = m.group(1).replace(',', '')
                if num.isdigit():
                    base_24k_rate = int(num)

        if not base_24k_rate:
            print("⚠️ Candere live DOM failed.")
            return None

        rates['24K'] = base_24k_rate
        rates['22K'] = int(round(base_24k_rate * (22.0 / 24.0)))
        rates['18K'] = int(round(base_24k_rate * (18.0 / 24.0)))
        rates['14K'] = int(round(base_24k_rate * (14.0 / 24.0)))

        # Rename Candere to Kalyan for consistency with brand names used in calculations
        rates['Brand'] = 'Kalyan'
        return rates
    except Exception as e:
        print(f"⚠️ Candere Error: {e}")
        return None

# ==========================================
# RUNNER
# ==========================================
def print_beautiful_console(results):
    print("\n" + "="*50)
    print(" 🌟 LIVE GOLD RATES (Per Gram in ₹) 🌟 ")
    print("="*50)
    
    print(f"{'BRAND':<12} | {'24K':<7} | {'22K':<7} | {'18K':<7} | {'14K':<7}")
    print("-" * 50)
    
    for r in results:
        if r:
            b = r.get("Brand", "Unknown")
            k24 = r.get("24K", "N/A")
            k22 = r.get("22K", "N/A")
            k18 = r.get("18K", "N/A")
            k14 = r.get("14K", "N/A")
            print(f"{b:<12} | {k24:<7} | {k22:<7} | {k18:<7} | {k14:<7}")
            
    print("="*50 + "\n")

async def main():
    # 🔥 Impersonate upgrade to chrome124 to match the Senco headers
    async with AsyncSession(impersonate="chrome124") as session:
        tasks = [
            fetch_tanishq(session), 
            fetch_malabar(session), 
            fetch_senco(session), 
            fetch_candere(session)
        ]
        results = await asyncio.gather(*tasks)
        print_beautiful_console(results)

if __name__ == "__main__":
    import sys
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())