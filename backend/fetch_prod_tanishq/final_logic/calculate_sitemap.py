from curl_cffi import requests
import re
import json

def get_urls_from_sitemap(sitemap_url, session):
    print(f"📡 Processing: {sitemap_url}")
    try:
        # Use our spoofed Chrome session to fetch the XML
        response = session.get(sitemap_url)
        
        # 🛑 Check if the firewall blocked us so we aren't blind!
        if response.status_code != 200:
            print(f"⚠️ Server returned Status Code {response.status_code}. We got blocked.")
            return []

        # Use Regex to instantly rip out everything between <loc> and </loc>
        # This completely bypasses BeautifulSoup XML namespace bugs
        urls = re.findall(r'<loc>(.*?)</loc>', response.text)
        
        # Filter to keep only the jewelry products
        product_links = [u for u in urls if '/product/' in u]
        return product_links

    except Exception as e:
        print(f"❌ Error reading {sitemap_url}: {e}")
        return []

def main():
    print("🚀 Initializing the TLS-Spoofed Sitemap Harvester...")
    
    # Set up our Chrome 120 disguise
    session = requests.Session(impersonate="chrome120")
    
    # Hit the homepage first to grab the trusted human cookies
    print("🌐 Grabbing session cookies...")
    session.get('https://www.tanishq.co.in/')

    sub_sitemaps = [
        "https://www.tanishq.co.in/sitemap_0.xml",
        "https://www.tanishq.co.in/sitemap_1.xml",
        "https://www.tanishq.co.in/sitemap_2.xml"
    ]
    
    master_product_list = []

    for sitemap in sub_sitemaps:
        links = get_urls_from_sitemap(sitemap, session)
        master_product_list.extend(links)
        print(f"✅ Found {len(links)} products in this chunk.\n")

    # Remove any accidental duplicates
    unique_products = list(set(master_product_list))
    
    print(f"=========================================")
    print(f"🎉 TOTAL HARVESTED: {len(unique_products)} products!")
    print(f"=========================================")

    # Save to your JSON file
    with open('tanishq_full_database_urls.json', 'w') as f:
        json.dump(unique_products, f, indent=2)
    print("💾 Saved all URLs to 'tanishq_full_database_urls.json'")

if __name__ == "__main__":
    main()