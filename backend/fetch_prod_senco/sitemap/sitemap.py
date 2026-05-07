import asyncio
import os
import sys
import time
import json
from curl_cffi.requests import AsyncSession
from rich import print as rprint
from rich.progress import Progress, SpinnerColumn, TextColumn

# 🚀 UTILS INTEGRATION
root_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if root_path not in sys.path:
    sys.path.append(root_path)

from utils import detect_category

CATEGORIES_TO_FETCH = [
    "wristlet", "diamond jewellery", "gold jewellery", "venus collection diamond",
    "kids collection", "magnificence collection diamond", "victoria collection diamond",
    "tribe collection diamond", "vivaha collection", "bengal art collection gold",
    "denim collection gold", "coins and bars", "aham collection", "benarasi collection",
    "noorejashan", "colors collection", "pride collection", "yatra collection",
    "prime collection", "perfect love collection", "love collection", "lubdub collection",
    "deccan queen collection", "floral collection", "premium accessories", "cufflink",
    "traditional signature collection", "coconut shell collection", "utensils",
    "all products", "kashmir collection", "platinum jewellery", "composite collection",
    "daisy collection", "mayurpankh collection", "shakuntala devi collection",
    "aqua collection", "bandhan collection", "freedom collection", "astro based ring",
    "ya devi collection", "online gold booking", "shagun collection",
    "diamond pendant for week", "diamond earrings week", "diamond nosepin for week",
    "valentines special", "silver ornaments", "senco scheme", "valentines special 2k21",
    "good friday easter egg special", "customers favourite", "eid special 2022",
    "everlite collection", "mens jewellery", "retro classics", "platinum and gold mens chain",
    "gold and platinum diamond ring", "vintage collection", "doctors day special",
    "bridal package", "nosepin gold", "onam special", "gold and diamond rings",
    "gold and diamond bangle", "teachers day special 2021", "senco di wedding",
    "senco di wedding for bride and groom", "senco di wedding for old couples",
    "evara platinum", "senco di wedding for bride", "senco di wedding for groom",
    "senco di wedding for brother and sister", "gold and diamond necklace",
    "gold and diamond bracelets", "gold and diamond nosepins", "gold and diamond pendants",
    "gold and diamond earrings", "nova collection", "gifts", "gifts under 10k",
    "gifts for her", "gifts for him", "gift alphabet pendant", "gift silver",
    "gift coins and bars", "gift solitaires", "gift necklace", "vivaha collection 2022",
    "necklace and earrings flash sale", "gudi padwa special", "ugadi special",
    "heeray manik collection", "men of platinum", "milon collection", "diamond noa and bracelet",
    "polki collection", "teej special", "tria collection", "festive special 2022",
    "everlite festive collection", "durga puja jewellery collection", "tropica collection",
    "rajwada collection", "special offer", "love 2023", "i do collection", "sutra collection",
    "womens day special", "rings gold", "ear rings gold", "pendant gold", "necklace gold",
    "chain gold", "bangle gold", "bracelet gold", "pendant diamond", "nose pin diamonds",
    "earring diamond", "ring diamond", "necklace diamond", "bracelet diamond",
    "casual ring diamond", "cocktail ring diamond", "casual ring gold", "cocktail ring gold",
    "studs earring diamond", "studs earring gold", "drops earring diamond", "drops earring gold",
    "jhumki earring gold", "chandbali earring gold", "sitahar necklace gold",
    "floral necklace gold", "sankha bangle gold", "pola bangle gold", "noa bangle gold",
    "chur bangle gold", "bala pipe kada", "mantasha bracelet gold", "modern fancy bracelet gold",
    "modern fancy bracelet diamond", "shell pendant gold", "fancy pendant gold",
    "modern fancy chains gold", "fancy pendant diamond", "coin", "bar", "casual nosepin diamond",
    "kaan", "pendant set", "braceletdiamond", "bracelet platinum", "platinum bangle",
    "platinum churi", "platinum chains", "platinum fancy chains", "platinum ring",
    "platinum engagement ring", "platinum cocktail ring", "platinum earring",
    "platinum stud earring", "platinum drop earring", "platinum necklace", "platinum pendants",
    "platinum fancy pendant", "coin pendant", "designer pens", "gold utensils",
    "silver utensils", "gents astro based ring", "ladies astro based ring", "engagement ring gold",
    "spiral ring gold", "boat ring", "umbrella ring gold", "nailpolish ring gold",
    "baby ring gold", "makri earrings gold", "baby earrings gold", "god pendant gold",
    "baby pendant gold", "handmade chain gold", "machine made chain gold", "tienecklace gold",
    "choker necklace gold", "sleek necklace gold", "lahari necklace gold", "necklace set gold",
    "kankan bala gold", "churi gold", "ratan chur gold", "charmslet gold",
    "engagement ring diamond", "fancy necklace platinum", "chain pendant platinum",
    "sleek necklace platinum", "double chain platinum", "charmslet platinum",
    "platinum wristlet", "fancy bracelet platinum", "fancy necklace gold",
    "double loop pendant gold", "mens ring gold", "polki necklace", "baby pendant diamond",
    "god pendant diamond", "baby earrings diamond", "wristlet diamond", "fancy nosepin diamond",
    "gold nosepin", "gold nath", "gold bajubandh", "mangalsutra diamond", "alphabet pendant",
    "green pola", "bengali wedding", "north indian wedding", "bihari wedding",
    "kannada wedding", "telegu wedding", "muslim wedding", "upto 6 lac", "upto 12 lac",
    "upto 5 lac", "upto 9 lac", "diamond bangle", "diamond pola", "diamond noa",
    "baby chain", "churi diamond", "tushi necklace", "mens ring diamond",
    "bracelet customer favourite", "earrings customer favourite", "necklace customer favourite",
    "nosepin customer favourite", "pendant customer favourite", "pendant set customer favourite",
    "accessories all products", "bangle all products", "bracelet all products",
    "chain all products", "earrings all products", "mangalsutra all products",
    "necklace all products", "nosepin all products", "pendant all products",
    "pendant set all products", "ring all products", "wristlet all products",
    "party necklace diamond", "wedding necklace diamond", "gifts under 10k pendant",
    "gifts under 10k ring", "gifts under 10k nosepin", "gifts under 10k earrings",
    "gifts under 10k bracelet", "gifts under 10k bangle", "gifts for her pendant",
    "gifts for her earrings", "gifts for her nosepin", "gifts for her ring",
    "gifts for her bracelet", "gifts for her bangle", "gifts for her chain pendant",
    "gifts for her jewellery set", "gifts for her necklace", "gifts for her mangtika",
    "gifts for him pendant", "gifts for him accesories", "gifts for him ring",
    "gifts for him wristlet", "gifts for him chain", "gift solitaires ring",
    "gift solitaires earrings", "gift solitaires pendant", "gift solitaires nosepin",
    "pola necklace", "bracelet nova collection", "chain pendant nova collection",
    "earrings nova collection", "chain aham collection", "pendant aham collection",
    "accessories aham collection", "ring aham collection", "wristlet aham collection",
    "bangle yatra collection", "bracelet yatra collection", "earrings yatra collection",
    "necklace yatra collection", "pendant yatra collection", "pendant set yatra collection",
    "ring yatra collection", "earrings vintage collection", "pendant vintage collection",
    "ring vintage collection", "earrings signature collection", "earrings deccan queen collection",
    "bracelet victoria collection", "earrings victoria collection", "necklace victoria collection",
    "pendant victoria collection", "ring victoria collection", "pendant mayurpankh collection",
    "ring mayurpankh collection", "earrings perfect love collection",
    "mangalsutra perfect love collection", "nosepin perfect love collection",
    "pendant perfect love collection", "ring perfect love collection", "bangle evara platinum",
    "bracelet evara platinum", "chain evara platinum", "earrings evara platinum",
    "necklace evara platinum", "pendant evara platinum", "ring evara platinum",
    "earrings love collection", "pendant love collection", "ring love collection",
    "earrings freedom collection", "pendant freedom collection", "ring freedom collection",
    "pendant aqua collection", "ring aqua collection", "earrings denim collection",
    "pendant denim collection", "bracelet daisy collection", "pendant daisy collection",
    "ring daisy collection", "earrings magnificience collection",
    "pendant magnificience collection", "bracelet ya devi collection",
    "earrings ya devi collection", "pendant ya devi collection", "ring ya devi collection",
    "necklace tribe collection", "earrings tribe collection", "earrings floral collection",
    "pendant floral collection", "ring floral collection", "earrings venus collection",
    "pendant venus collection", "earrings colors collection", "pendant colors collection",
    "ring colors collection", "earrings coconut shell collection",
    "pendant set coconut shell collection", "pendant coconut shell collection",
    "accessories kids collection", "bangle kids collection", "earrings kids collection",
    "pendant kids collection", "ring kids collection", "bangle bengali wedding",
    "earrings bengali wedding", "necklace bengali wedding", "nosepin bengali wedding",
    "pendant bengali wedding", "ring bengali wedding", "bangle north indian wedding",
    "bracelet north indian wedding", "earrings north indian wedding",
    "necklace north indian wedding", "pendant set north indian wedding",
    "pendant north indian wedding", "ring north indian wedding", "earrings bihari wedding",
    "necklace bihari wedding", "ring bihari wedding", "bangle kannada wedding",
    "earrings kannada wedding", "necklace kannada wedding", "bangle telegu wedding",
    "earrings telegu wedding", "necklace telegu wedding", "earrings muslim wedding",
    "necklace muslim wedding", "ginkgo collection", "pola ring gold", "belt", "brooch", "button",
    "cufflink premium accessories", "tie pin", "spoon", "bowl", "glass", "plate", "cup", "kalash",
    "idol", "mangaldeep", "diya", "kajal lota", "sindoor dani", "throne", "sruti collection",
    "mangalsutras gold", "bangle utsav collection", "evil eye collection", "22kt jewellery",
    "mariposa collection", "cera collection", "spectra collection", "shakti collection",
    "lotus collection", "power collection", "ganesh chaturthi special", "earrings festival",
    "diamond chain", "puja utensils", "bala bangle utsav collection",
    "churi bangle utsav collection", "bracelet bangle utsav collection",
    "mens wristlet bangle utsav collection", "noa bangle utsav collection",
    "charmslet bangle utsav collection", "sankha bangle utsav collection",
    "pola bangle utsav collection", "chur bangle utsav collection", "mens ring platinum",
    "satya prem ki katha", "gold chain pendant", "alphabet pendant diamond",
    "mangalsutra customer favourite", "lord ganesh", "goddess laxmi", "laxmi ganesh",
    "laxmi narayan", "bal gopal", "signature collection", "bracelet tribe collection",
    "pendant tribe collection", "earrings mariposa collection", "necklace mariposa collection",
    "ring mariposa collection", "chain pendant mariposa collection", "bracelet mariposa collection",
    "ring venus collection", "bracelet venus collection", "bracelet denim collection",
    "chain pendant denim collection", "necklace love collection", "bracelet love collection",
    "chain pendant love collection", "ring ginkgo collection", "earrings ginkgo collection",
    "pendant ginkgo collection", "bracelet ginkgo collection", "necklace ginkgo collection",
    "necklace tria collection", "earrings tria collection", "earrings tropica collection",
    "pendant tropica collection", "ring tropica collection", "necklace tropica collection",
    "chain pendant tropica collection", "pendant love 2023", "earrings love 2023", "ring love 2023",
    "chain pendant love 2023", "ring cera collection", "earrings cera collection",
    "pendant cera collection", "earrings evil eye collection", "pendant evil eye collection",
    "ring evil eye collection", "bracelet evil eye collection", "chain pendant evil eye collection",
    "earrings spectra collection", "necklace spectra collection", "ring spectra collection",
    "chain pendant spectra collection", "bracelet spectra collection", "earrings lotus collection",
    "pendant lotus collection", "ring lotus collection", "chain pendant lotus collection",
    "earrings power collection", "pendant power collection", "ring power collection",
    "pendant shakti collection", "earrings shakti collection", "ring shakti collection",
    "necklace shakti collection", "bracelet shakti collection", "chain pendant shakti collection",
    "mangalsutra signature collection", "chain pendant signature collection",
    "ring signature collection", "necklace shagun collection", "earrings shagun collection",
    "ring shagun collection", "bangle shagun collection", "bracelet shagun collection",
    "necklace radwada collection", "earrings rajwada collection", "ring rajwada collection",
    "bangle rajwada collection", "bracelet rajwada collection", "sankha bangle rajwada collection",
    "pola bangle rajwada collection", "necklace satyaprem ki katha", "earrings satyaprem ki katha",
    "bangle satyaprem ki katha", "necklace milon collection", "earrings milon collection",
    "ring milon collection", "pendant spectra collection", "pendant mariposa collection",
    "bangle mariposa collection", "necklace rajwada collection", "mangtika rajwada collection",
    "hermosa collection", "diamond hoop earrings", "bangle everlite collection",
    "bracelet everlite collection", "chain everlite collection", "chain pendant everlite collection",
    "earrings everlite collection", "mangalsutra everlite collection",
    "necklace everlite collection", "nose pin everlite collection", "pendant everlite collection",
    "pendant set everlite collection", "ring everlite collection", "wristlet everlite collection",
    "earrings hermosa collection", "pendant hermosa collection", "earrings sruti collection",
    "siyaram collection", "necklace siyaram collection", "pendant siyaram collection",
    "chain pendant siyaram collection", "earrings siyaram collection", "festival of love",
    "chain pendant tria collection", "ring tria collection", "romantique collection", "love 2024",
    "bangle siyaram collection", "earrings romantique collection", "necklace romantique collection",
    "bracelet love 2024", "chain pendant love 2024", "earrings love 2024", "pendant love 2024",
    "ring love 2024", "men gold chain", "women gold chain", "unisex gold chain",
    "men platinum chain", "women platinum chain", "unisex platinum chain", "men diamond chain",
    "unisex diamond chain", "ribbon collection", "bracelet ribbon collection",
    "bangle ribbon collection", "chain pendant ribbon collection", "earrings ribbon collection",
    "ring ribbon collection", "terracotta collection", "pendant terracotta collection",
    "earrings terracotta collection", "ring terracotta collection", "modern gold mangalsutra",
    "traditional gold mangalsutra", "floral gold mangalsutra", "eid special",
    "modern diamond mangalsutra", "traditional diamond mangalsutra", "solitaire diamond mangalsutra",
    "floral diamond mangalsutra", "diamond solitaire earrings", "diamond solitaire rings",
    "diamond solitaire pendants", "gathbandhan collection", "bangle gathbandhan collection",
    "earrings gathbandhan collection", "necklace gathbandhan collection", "ring gathbandhan collection",
    "wristlet gathbandhan collection", "pleat collection", "earrings pleat collection",
    "ring pleat collection", "pendant pleat collection", "bracelet pleat collection",
    "chain pendant pleat collection", "mens pendant diamond", "mens pendant gold",
    "kada aham collection", "gold maang tikka", "queen bee collection", "pendant queen bee collection",
    "bracelet queen bee collection", "ring queen bee collection", "earring queen bee collection",
    "mens kada platinum", "chain festival", "chain pendant diamond", "women jewellery",
    "chain pendant all products", "beans", "god pendant platinum", "aparupa collection",
    "earrings for women", "pendant for women", "necklace for women", "chain pendant for women",
    "ring for women", "bracelets for women", "bangle for women", "chain for women",
    "mangalsutra for women", "maang tikka", "nose pin for women", "nath", "bracelets lotus collection",
    "pendant shagun collection", "regalia collection", "gold coins bars and beans",
    "silver coins and bars", "vivaah collection", "diamond men's earrings", "zodiac collection",
    "ring and earrings all products", "chain and mangalsutra", "vivaah collection necklace",
    "vivaah collection earrings", "vivaah collection ring", "vivaah collection maang tikka",
    "vivaah collection bracelet", "expressions of love", "berry lovely collection",
    "facets of love collection", "ice cube collection", "valentines special diamond collection",
    "rose collection", "ombre collection", "silver products", "polki all products", "watch",
    "aham platinum", "infinity collection", "lord hanuman", "golden curve collection",
    "golden curve collection earrings", "golden curve collection necklace",
    "golden curve collection pendant", "vivaah collection bangle", "vivaah collection chain",
    "ombre collection earrings", "ombre collection rings", "ombre collection pendant",
    "ombre collection bracelet", "infinity collection earrings", "infinity collection chain pendant",
    "facets of love collection rings", "facets of love collection earrings",
    "facets of love collection pendant", "nayiraah collection", "nayiraah collection necklace",
    "nayiraah collection earrings", "berry lovely collection earrings",
    "berry lovely collection necklace", "berry lovely collection rings",
    "valentine's special diamond collection bracelet", "valentine's special diamond collection bangle",
    "valentine's special diamond collection rings", "valentine's special diamond collection wristlet",
    "valentine's special diamond collection pendant", "valentine's special diamond collection earrings",
    "valentine's special diamond collection necklace", "rose collection bracelet",
    "rose collection earrings", "rose collection rings", "rose collection chain pendant",
    "ice cube collection rings", "ice cube collection pendant", "ice cube collection earrings",
    "daily wear diamond earrings", "daily wear gold earrings", "simple gold necklace",
    "simple diamond necklace", "simple diamond ring", "3 gram gold earrings",
    "light weight gold earrings", "antique gold necklace", "gold earcuffs", "gold kada for women",
    "gold rings for couple", "sui dhaga earrings", "rose gold earring", "kundan earrings",
    "one gram gold earrings", "rakhi all products", "rakhi collection", "raksha bandhan bracelet pendant",
    "teej jewellery", "0.5 gm gold coin", "1 gm gold coin", "2 gm gold coin", "5 gm gold coin",
    "10 gm gold coin", "20 gm gold coin", "50 gm silver coin", "100 gm silver coin",
    "500 gm silver coin", "varalaxmi collections", "elements of nature", "man of platinum",
    "9kt jewellery", "18kt jewellery", "14kt jewellery", "princess cut diamond engagement ring",
    "heart shaped diamond ring", "oval diamond ring", "square diamond ring",
    "princess cut engagement ring", "oval engagement ring", "round cut engagement rings",
    "round engagement ring", "pear shape diamond ring", "pear diamond engagement ring",
    "cushion cut diamond ring", "cushion cut diamond engagement rings", "silver jewellery",
    "silver jewellery men", "silver jewellery women", "silver bracelet women", "silver rings women",
    "silver earrings women", "silver chain mens", "silver anklets", "mens silver ring",
    "ganesha pendant gold", "rose gold jewellery", "gold studs men", "diamond mens earrings",
    "navratri durga puja jewellery", "onam jewellery", "ganesh locket gold", "teachers day gift",
    "diwali gift ideas", "akshaya tritiya gold offers", "diwali jewellery", "silver bowl", "bowl gold",
    "cup silver", "diya silver", "diya stand silver", "glass silver", "kalash silver", "mukut silver",
    "plate silver", "pooja jhula silver", "sindoor dani silver", "spoon silver", "spoon gold",
    "utensils silver", "utensils gold", "heart shaped engagement ring", "diamond button",
    "diamond cufflink", "diamond tie pin", "gold brooch", "gold buckle", "gold cufflink",
    "gold tie pin", "platinum watch", "silver mall", "premium accessories diamond",
    "premium accessories gold", "premium accessories platinum", "premium accessories silver",
    "durga puja navratri jewellery", "cloud9 collection", "elements of love", "2 gram gold earrings",
    "4 gram gold earrings", "5 gram gold earrings", "10 gram gold jhumka", "5 gram gold jhumka",
    "10 gram gold mangalsutra", "20 gram gold mangalsutra", "valentines day gifts",
    "valentines day gifts for him", "valentines day gifts for her",
    "valentines day gifts for boyfriend", "valentines day gifts for girlfriend", "jiostar special",
    "a initial gold pendant", "s initial gold pendant", "5 gram gold chain", "7 gram gold chain",
    "6 gram gold chain", "8 gram gold chain", "versa collection", "earrings for haldi",
    "haldi maang tika", "necklace for haldi", "haldi bangles", "bridal earrings",
    "heavy gold earrings for wedding", "light weight gold jewellery", "light weight gold chain",
    "light weight gold necklace", "light weight gold bangle", "light weight mangalsutra",
    "light weight gold pendant", "bangle utsav2026", "chur bangle platinum", "silver all products"
]
async def fetch_category_from_api(session, category_name, progress, task_id):
    """Ek specific category ko Unbxd API se fetch karta hai jab tak pages khatam na ho jayein."""
    category_products = []
    page = 1
    rows = 100  # API usually allows max 100 rows per request
    
    current_time = int(time.time() * 1000)
    uid = f"uid-{current_time}-48347"
    
    while True:
        # Notice: yahan hum q={category_name} bhej rahe hain
        api_url = f"https://search.unbxd.io/2f0815a68672fd25b4b7992b72302e5b/ss-unbxd-aapac-prod-sencogold56671721125516/search?q={category_name}&rows={rows}&page={page}&uid={uid}&fields=title,sku,productUrl"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Origin': 'https://sencogoldanddiamonds.com',
            'Referer': 'https://sencogoldanddiamonds.com/'
        }
        
        try:
            # Impersonate 'chrome120' to avoid Cloudflare/API blocks
            response = await session.get(api_url, headers=headers, impersonate="chrome120", timeout=20)
            
            if response.status_code != 200:
                break
                
            json_data = response.json()
            items = json_data.get('response', {}).get('products', [])
            
            if not items:
                break # Agar items aane band ho gaye, toh ye category khatam
                
            for item in items:
                sku = item.get('sku')
                title = item.get('title', '')
                raw_url = item.get('productUrl', '')
                full_url = raw_url if raw_url.startswith('http') else f"https://sencogoldanddiamonds.com/{raw_url.lstrip('/')}"
                
                category_products.append({
                    "Brand": "Senco",
                    "product_url": full_url,
                    "sku": sku,
                    "title": title,
                    "category": detect_category(title)
                })
            
            progress.update(task_id, description=f"[cyan]📦 {category_name.capitalize()}: Page {page} fetched ({len(category_products)} items)...")
            page += 1 
            
            # API ko thoda saans lene do taaki block na kare
            await asyncio.sleep(0.5)
            
        except Exception as e:
            # rprint(f"[red]Error fetching {category_name} page {page}: {e}[/red]")
            break
            
    return category_products

async def fetch_all_senco_urls_fast():
    rprint("\n[bold blue]🚀 Firing Async Unbxd API (Limit-Bypass Mode)...[/bold blue]\n")
    
    all_products = []
    unique_skus = set()
    output_file = "senco_links_new.json"

    # ==========================================
    # 🆕 THE JSON DUPLICATE CHECKER LOGIC
    # ==========================================
    if os.path.exists(output_file):
        try:
            with open(output_file, "r", encoding="utf-8") as f:
                existing_data = json.load(f)
                all_products.extend(existing_data) # Pura purana data list mein daal lo
                for item in existing_data:
                    if item.get("sku"):
                        unique_skus.add(item["sku"])
            rprint(f"[bold yellow]📂 Found existing file! Loaded {len(unique_skus)} unique SKUs to memory.[/bold yellow]")
        except json.JSONDecodeError:
            rprint("[bold red]⚠️ Existing JSON is empty or invalid. Starting fresh.[/bold red]")
    else:
        rprint("[bold cyan]📁 No existing JSON file found. Starting fresh.[/bold cyan]")

    initial_count = len(unique_skus)

    # ... Baki ka Progress Bar aur Async logic same rahega ...
    
    with Progress(
        SpinnerColumn("bouncingBar", style="yellow"),
        TextColumn("[progress.description]{task.description}"),
    ) as progress:
        
        async with AsyncSession() as session:
            tasks = []
            for cat in CATEGORIES_TO_FETCH:
                task_id = progress.add_task(f"[cyan]⏳ Starting {cat}...", total=None)
                tasks.append(fetch_category_from_api(session, cat, progress, task_id))
            
            results = await asyncio.gather(*tasks)
            
            # 🆕 CHECKER: Pushing only fresh data
            new_items_added = 0
            for category_result in results:
                for item in category_result:
                    if item['sku'] and item['sku'] not in unique_skus:
                        unique_skus.add(item['sku'])
                        all_products.append(item)
                        new_items_added += 1

    rprint(f"\n[bold green]🎉 SUCCESS: Extracted {new_items_added} NEW URLs![/bold green]")
    return all_products

if __name__ == "__main__":
    if os.name == 'nt':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        
    start_time = time.time()
    products = asyncio.run(fetch_all_senco_urls_fast())
    end_time = time.time()
    
    if products:
        with open("senco_links_new.json", "w", encoding="utf-8") as f:
            json.dump(products, f, indent=4)
            
        rprint("\n[bold green]" + "="*60 + "[/bold green]")
        rprint(f"[bold white on green] ✅ SITEMAP COMPLETE! Fetched {len(products)} Unique Items. [/bold white on green]")
        rprint(f"[bold cyan] ⏱️ Time taken: {round(end_time - start_time, 2)} seconds [/bold cyan]")
        rprint("[bold green]" + "="*60 + "[/bold green]\n")