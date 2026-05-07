import json
import os
import time
from urllib import response # Added for a small delay to avoid timeout
from curl_cffi import requests

from selectolax.parser import HTMLParser


def main():
    output_file = 'tanishq_earrings_urls.json'
    all_product_urls = set()
    
    # ---------------------------------------------------------
    # 🆕 CHECKER LOGIC: Load existing URLs from JSON if it exists
    # ---------------------------------------------------------
    if os.path.exists(output_file):
        with open(output_file, 'r') as f:
            try:
                existing_urls = json.load(f)
                all_product_urls.update(existing_urls) # Sets automatically handle duplicates
                print(f"📂 Found existing file! Loaded {len(existing_urls)} URLs to memory.")
            except json.JSONDecodeError:
                print("⚠️ Existing JSON is empty or invalid. Starting fresh.")
    else:
        print("📁 No existing JSON file found. Starting fresh.")
        
    initial_url_count = len(all_product_urls)
    
    start = 0
    size = 300
    has_more_products = True
    TEST_LIMIT = 30000 # 🛑 The hard limit for testing

    print("\n🚀 Initializing the TLS-Spoofing Harvester...")
    session = requests.Session(impersonate="chrome120")

    print("🌐 Grabbing session cookies...")
    session.get('https://www.tanishq.co.in/shop/jewellery?lang=en_IN')

    while has_more_products:
        print(f"📡 Fetching items {start} to {start + size}...")
        
        target_url = f"https://www.tanishq.co.in/on/demandware.store/Sites-Tanishq-Site/en_IN/Search-UpdateGrid?cgid=tq-all-jewellery&prefn1=priceRecordMissing&prefv1=false&start={start}&sz={size}&selectedUrl=https%3A%2F%2Fwww.tanishq.co.in%2Fon%2Fdemandware.store%2FSites-Tanishq-Site%2Fen_IN%2FSearch-UpdateGrid%3Fcgid%3Dtq-all-jewellery%26prefn1%3DpriceRecordMissing%26prefv1%3Dfalse%26start%3D24%26sz%3D24&isFestivePLP=false&isPlpWithSlots=false&isPlpWithCompare=false"
        
        try:
            # Added timeout=60 here as discussed previously
            response = session.get(target_url, timeout=60, headers={
                'X-Requested-With': 'XMLHttpRequest',
                'Referer': 'https://www.tanishq.co.in/shop/jewellery?lang=en_IN'
            })
        except Exception as e:
            print(f"❌ Network Error on items {start} to {start + size}: {e}")
            break # Exit the loop safely to save whatever we have so far

        if response.status_code == 403:
            print("⚠️ Blocked by WAF (403).")
            break


        # Inside your loop:
        tree = HTMLParser(response.text)
# CSS selectors in selectolax are lightning fast
        links = [node.attributes.get('href') for node in tree.css('a') if node.attributes.get('href')]
        product_links = [link for link in links if '/product/' in link]

        
        if not product_links:
            print("🏁 Reached the end of the catalog.")
            break

        new_urls_in_this_batch = 0
        for link in product_links:
            full_url = link if link.startswith('http') else f"https://www.tanishq.co.in{link}"
            
            # 🆕 CHECKER: Agar URL pehle se set mein hai, toh ignore karo
            if full_url in all_product_urls:
                continue
                
            all_product_urls.add(full_url)
            new_urls_in_this_batch += 1

        print(f"   -> Added {new_urls_in_this_batch} new unique URLs.")

        if len(all_product_urls) >= TEST_LIMIT:
            print(f"🛑 Reached test limit of {TEST_LIMIT} URLs. Stopping harvester.")
            break

        start += size
        
        # Adding a tiny delay (1 second) so we don't bombard the server and get timed out
        time.sleep(1)

    unique_urls = list(all_product_urls)[:TEST_LIMIT]
    new_urls_total = len(unique_urls) - initial_url_count
    
    print(f"\n🎉 SUCCESS: Extracted {new_urls_total} NEW URLs! (Total URLs now: {len(unique_urls)})")
    
    with open(output_file, 'w') as f:
        json.dump(unique_urls, f, indent=2)
        
    print(f"💾 Saved URLs safely to '{output_file}'")

if __name__ == '__main__':
    main()