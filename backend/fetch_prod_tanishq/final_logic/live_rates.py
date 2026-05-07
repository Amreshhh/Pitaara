import re
from curl_cffi import requests
from selectolax.parser import HTMLParser

def get_live_22k_rate():
    """Sirf 22K ka rate fetch karega Tanishq se."""
    url = "https://www.tanishq.co.in/gold-rate.html?lang=en_IN"
    
    try:
        response = requests.get(url, impersonate="chrome120", timeout=15)
        if response.status_code != 200:
            return None

        tree = HTMLParser(response.text)
        
        # Sirf 22K wali table target kar rahe hain
        table = tree.css_first('.goldrate-table-22kt')
        if table:
            rows = table.css('tbody tr')
            for row in rows:
                cells = row.css('td')
                if len(cells) >= 2 and '1 g' in cells[0].text(strip=True).lower():
                    raw_price = cells[1].text(strip=True)
                    match = re.search(r'([\d,]+)', raw_price)
                    if match:
                        return int(match.group(1).replace(',', ''))
        return None
        
    except Exception as e:
        print(f"⚠️ Gold Rate Fetch Error: {e}")
        return None

if __name__ == "__main__":
    rate = get_live_22k_rate()
    print(f"💰 Aaj ka 22K Gold Rate: ₹ {rate}" if rate else "❌ Fetch fail ho gaya")