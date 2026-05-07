import json
import asyncio
import re
from curl_cffi.requests import AsyncSession

# 🛠️ HELPER: URL ke liye naam ko saaf karna (e.g., "Lovable Gold Earrings" -> "lovable-gold-earrings")
def format_url_name(name):
    clean = re.sub(r'[^a-zA-Z0-9\s-]', '', name).strip().lower()
    return re.sub(r'\s+', '-', clean)

async def fetch_page(session, current_page, page_size, semaphore):
    api_url = 'https://www.malabargoldanddiamonds.com/graphql-magento'
    
    # 🚀 NAYA: Barcode bhi mangwa rahe hain URL mein daalne ke liye
    graphql_query = """
   query products($filter: ProductAttributeFilterInput, $pageSize: Int, $currentPage: Int) {
  products(filter: $filter, pageSize: $pageSize, currentPage: $currentPage) {
    items {
      name
      sku
      # 🚀 ASLI JADOO YAHAN HAI: 
      # Humne list ke items ke andar hi unki andar ki details maang li!
      price_breakup {
        purity
        net_weight
        gross_weight
        metal_charges
        diamond_charges
        stone_charges
        other_stone
        making_charges
        tax
        total
      }
    }
    total_count
    page_info {
      page_size
      current_page
      total_pages
    }
  }
}
    """
    
    variables_dict = {
        "pageSize": page_size,
        "currentPage": current_page,
        "filter": {"malabar_product_type": {"in": ["99"]}} # Apni category ID daal lena
    }

    params = {
        "query": graphql_query,
        "variables": json.dumps(variables_dict)
    }

    # Asynchronous request ke time hum Semaphore use karte hain taaki WAF block na kare
    async with semaphore:
        print(f"⏳ Fetching Page {current_page}...")
        try:
            response = await session.get(
                api_url,
                params=params,
                impersonate="chrome120",
                timeout=20
            )

            if response.status_code != 200:
                print(f"❌ Page {current_page} Blocked! Status: {response.status_code}")
                return []

            data = response.json()
            items = data.get("data", {}).get("products", {}).get("items", [])
            
            page_products = []
            for item in items:
                sku = item.get("sku", "")
                name = item.get("name", "malabar-product")
                
                # Barcode nikalne ka logic
                barcode = ""
                breakup = item.get("price_breakup")
                if breakup and isinstance(breakup, list) and len(breakup) > 0:
                    barcode = breakup[0].get("barcode", "")

                formatted_name = format_url_name(name)
                
                # 🚀 TERA EXACT URL FORMAT YAHAN BAN RAHA HAI
                product_url = f"https://www.malabargoldanddiamonds.com/in/pan-india/en/product/{formatted_name}.html?sku={sku}&barcode={barcode}"

                page_products.append({
                    "sku": sku,
                    "product_url": product_url
                })
                
            print(f"✅ Page {current_page} Fetched! ({len(page_products)} items)")
            return page_products

        except Exception as e:
            print(f"⚠️ Error on page {current_page}: {e}")
            return []

async def main_async_scraper():
    page_size = 300  # Isko 200 try karke dekh lena agar server allow kare toh
    total_pages_to_scrape = 15 # Pehle test ke liye 15 pages (1500 products) scrape kar rahe hain
    
    all_products = []
    
    # Semaphore limit: Ek waqt par Cloudflare ko sirf 5 requests jayengi (Anti-ban system)
    semaphore = asyncio.Semaphore(7)
    
    headers = {
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Referer": "https://www.malabargoldanddiamonds.com/",
        "Origin": "https://www.malabargoldanddiamonds.com",
    }

    print("🚀 Starting ASYNC BULK Scraping...")

    # AsyncSession open karte hain
    async with AsyncSession(headers=headers) as session:
        # Saare pages ke tasks ek sath create kar diye
        tasks = []
        for page_num in range(1, total_pages_to_scrape + 1):
            task = fetch_page(session, page_num, page_size, semaphore)
            tasks.append(task)
            
        # Un saare tasks ko ek sath (concurrently) run kar diya
        results = await asyncio.gather(*tasks)
        
        # Results ek list of lists honge, unko single list mein jodna hai
        for page_result in results:
            all_products.extend(page_result)

    # 💾 SAVING DATA
    with open("malabar_async_links.json", "w", encoding="utf-8") as f:
        json.dump(all_products, f, indent=4)

    print("\n" + "="*50)
    print(f"🎉 ASYNC SUCCESS! Saved {len(all_products)} products to 'malabar_async_links.json'.")
    # print(f"📌 Sample URL: {all_products[0]['product_url'] if all_products else 'N/A'}")
    print("="*50)

# Python script ko normally run karne ke liye asyncio.run() ka use hota hai
if __name__ == "__main__":
    asyncio.run(main_async_scraper())