import asyncio
import json
import os
import sys
import time
import urllib.parse
from curl_cffi.requests import AsyncSession
from selectolax.parser import HTMLParser
from rich import print as rprint
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, TimeElapsedColumn

# 🚀 UTILS INTEGRATION
root_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if root_path not in sys.path:
    sys.path.append(root_path)

try:
    from utils import detect_category
except ImportError:
    # Fallback agar utils nahi mila
    def detect_category(title): return "Other"

# ==========================================
# 🚀 PASTE YOUR 816 RAW SITEMAP URLS HERE
# ==========================================
RAW_SITEMAP_URLS = [
    "https://sencogoldanddiamonds.com/jewellery/category/wristlet",
    "https://sencogoldanddiamonds.com/jewellery/category/diamond-jewellery",
    "https://sencogoldanddiamonds.com/jewellery/category/gold-jewellery",
    "https://sencogoldanddiamonds.com/jewellery/category/venus-collection-diamond",
    "https://sencogoldanddiamonds.com/jewellery/category/kids-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/magnificence-collection-diamond",
    "https://sencogoldanddiamonds.com/jewellery/category/victoria-collection-diamond",
    "https://sencogoldanddiamonds.com/jewellery/category/tribe-collection-diamond",
    "https://sencogoldanddiamonds.com/jewellery/category/vivaha-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/bengal-art-collection-gold",
    "https://sencogoldanddiamonds.com/jewellery/category/denim-collection-gold",
    "https://sencogoldanddiamonds.com/jewellery/category/coins-and-bars",
    "https://sencogoldanddiamonds.com/jewellery/category/aham-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/benarasi-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/noorejashan",
    "https://sencogoldanddiamonds.com/jewellery/category/colors-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/pride-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/yatra-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/prime-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/perfect-love-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/love-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/lubdub-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/deccan-queen-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/floral-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/premium-accessories",
    "https://sencogoldanddiamonds.com/jewellery/category/cufflink",
    "https://sencogoldanddiamonds.com/jewellery/category/traditional-signature-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/coconut-shell-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/utensils",
    "https://sencogoldanddiamonds.com/jewellery/category/all-products",
    "https://sencogoldanddiamonds.com/jewellery/category/kashmir-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/platinum-jewellery",
    "https://sencogoldanddiamonds.com/jewellery/category/composite-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/daisy-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/mayurpankh-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/shakuntala-devi-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/aqua-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/bandhan-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/freedom-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/astro-based-ring",
    "https://sencogoldanddiamonds.com/jewellery/category/ya-devi-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/online-gold-booking",
    "https://sencogoldanddiamonds.com/jewellery/category/shagun-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/diamond-pendant-for-week",
    "https://sencogoldanddiamonds.com/jewellery/category/diamond-earrings-week",
    "https://sencogoldanddiamonds.com/jewellery/category/diamond-nosepin-for-week",
    "https://sencogoldanddiamonds.com/jewellery/category/valentines-special",
    "https://sencogoldanddiamonds.com/jewellery/category/silver-ornaments",
    "https://sencogoldanddiamonds.com/jewellery/category/senco-scheme",
    "https://sencogoldanddiamonds.com/jewellery/category/valentines-special-2k21",
    "https://sencogoldanddiamonds.com/jewellery/category/good-friday-easter-egg-special",
    "https://sencogoldanddiamonds.com/jewellery/category/customers-favourite",
    "https://sencogoldanddiamonds.com/jewellery/category/eid-special-2022",
    "https://sencogoldanddiamonds.com/jewellery/category/everlite-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/mens-jewellery",
    "https://sencogoldanddiamonds.com/jewellery/category/retro-classics",
    "https://sencogoldanddiamonds.com/jewellery/category/platinum-and-gold-mens-chain",
    "https://sencogoldanddiamonds.com/jewellery/category/gold-and-platinum-diamond-ring",
    "https://sencogoldanddiamonds.com/jewellery/category/vintage-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/doctors-day-special",
    "https://sencogoldanddiamonds.com/jewellery/category/bridal-package",
    "https://sencogoldanddiamonds.com/jewellery/category/nosepin-gold",
    "https://sencogoldanddiamonds.com/jewellery/category/onam-special",
    "https://sencogoldanddiamonds.com/jewellery/category/gold-and-diamond-rings",
    "https://sencogoldanddiamonds.com/jewellery/category/gold-and-diamond-bangle",
    "https://sencogoldanddiamonds.com/jewellery/category/teachers-day-special-2021",
    "https://sencogoldanddiamonds.com/jewellery/category/senco-di-wedding",
    "https://sencogoldanddiamonds.com/jewellery/category/senco-di-wedding-for-bride-and-groom",
    "https://sencogoldanddiamonds.com/jewellery/category/senco-di-wedding-for-old-couples",
    "https://sencogoldanddiamonds.com/jewellery/category/evara-platinum",
    "https://sencogoldanddiamonds.com/jewellery/category/senco-di-wedding-for-bride",
    "https://sencogoldanddiamonds.com/jewellery/category/senco-di-wedding-for-groom",
    "https://sencogoldanddiamonds.com/jewellery/category/senco-di-wedding-for-brother-and-sister",
    "https://sencogoldanddiamonds.com/jewellery/category/gold-and-diamond-necklace",
    "https://sencogoldanddiamonds.com/jewellery/category/gold-and-diamond-bracelets",
    "https://sencogoldanddiamonds.com/jewellery/category/gold-and-diamond-nosepins",
    "https://sencogoldanddiamonds.com/jewellery/category/gold-and-diamond-pendants",
    "https://sencogoldanddiamonds.com/jewellery/category/gold-and-diamond-earrings",
    "https://sencogoldanddiamonds.com/jewellery/category/nova-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/gifts",
    "https://sencogoldanddiamonds.com/jewellery/category/gifts-under-10k",
    "https://sencogoldanddiamonds.com/jewellery/category/gifts-for-her",
    "https://sencogoldanddiamonds.com/jewellery/category/gifts-for-him",
    "https://sencogoldanddiamonds.com/jewellery/category/gift-alphabet-pendant",
    "https://sencogoldanddiamonds.com/jewellery/category/gift-silver",
    "https://sencogoldanddiamonds.com/jewellery/category/gift-coins-and-bars",
    "https://sencogoldanddiamonds.com/jewellery/category/gift-solitaires",
    "https://sencogoldanddiamonds.com/jewellery/category/gift-necklace",
    "https://sencogoldanddiamonds.com/jewellery/category/vivaha-collection-2022",
    "https://sencogoldanddiamonds.com/jewellery/category/necklace-and-earrings-flash-sale",
    "https://sencogoldanddiamonds.com/jewellery/category/gudi-padwa-special",
    "https://sencogoldanddiamonds.com/jewellery/category/ugadi-special",
    "https://sencogoldanddiamonds.com/jewellery/category/heeray-manik-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/men-of-platinum",
    "https://sencogoldanddiamonds.com/jewellery/category/milon-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/diamond-noa-and-bracelet",
    "https://sencogoldanddiamonds.com/jewellery/category/polki-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/teej-special",
    "https://sencogoldanddiamonds.com/jewellery/category/tria-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/festive-special-2022",
    "https://sencogoldanddiamonds.com/jewellery/category/everlite-festive-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/durga-puja-jewellery-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/tropica-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/rajwada-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/special-offer",
    "https://sencogoldanddiamonds.com/jewellery/category/love-2023",
    "https://sencogoldanddiamonds.com/jewellery/category/i-do-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/sutra-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/womens-day-special",
    "https://sencogoldanddiamonds.com/jewellery/category/rings-gold",
    "https://sencogoldanddiamonds.com/jewellery/category/ear-rings-gold",
    "https://sencogoldanddiamonds.com/jewellery/category/pendant-gold",
    "https://sencogoldanddiamonds.com/jewellery/category/necklace-gold",
    "https://sencogoldanddiamonds.com/jewellery/category/chain-gold",
    "https://sencogoldanddiamonds.com/jewellery/category/bangle-gold",
    "https://sencogoldanddiamonds.com/jewellery/category/bracelet-gold",
    "https://sencogoldanddiamonds.com/jewellery/category/pendant-diamond",
    "https://sencogoldanddiamonds.com/jewellery/category/nose-pin-diamonds",
    "https://sencogoldanddiamonds.com/jewellery/category/earring-diamond",
    "https://sencogoldanddiamonds.com/jewellery/category/ring-diamond",
    "https://sencogoldanddiamonds.com/jewellery/category/necklace-diamond",
    "https://sencogoldanddiamonds.com/jewellery/category/bracelet-diamond",
    "https://sencogoldanddiamonds.com/jewellery/category/casual-ring-diamond",
    "https://sencogoldanddiamonds.com/jewellery/category/cocktail-ring-diamond",
    "https://sencogoldanddiamonds.com/jewellery/category/casual-ring-gold",
    "https://sencogoldanddiamonds.com/jewellery/category/cocktail-ring-gold",
    "https://sencogoldanddiamonds.com/jewellery/category/studs-earring-diamond",
    "https://sencogoldanddiamonds.com/jewellery/category/studs-earring-gold",
    "https://sencogoldanddiamonds.com/jewellery/category/drops-earring-diamond",
    "https://sencogoldanddiamonds.com/jewellery/category/drops-earring-gold",
    "https://sencogoldanddiamonds.com/jewellery/category/jhumki-earring-gold",
    "https://sencogoldanddiamonds.com/jewellery/category/chandbali-earring-gold",
    "https://sencogoldanddiamonds.com/jewellery/category/sitahar-necklace-gold",
    "https://sencogoldanddiamonds.com/jewellery/category/floral-necklace-gold",
    "https://sencogoldanddiamonds.com/jewellery/category/sankha-bangle-gold",
    "https://sencogoldanddiamonds.com/jewellery/category/pola-bangle-gold",
    "https://sencogoldanddiamonds.com/jewellery/category/noa-bangle-gold",
    "https://sencogoldanddiamonds.com/jewellery/category/chur-bangle-gold",
    "https://sencogoldanddiamonds.com/jewellery/category/bala-pipe-kada",
    "https://sencogoldanddiamonds.com/jewellery/category/mantasha-bracelet-gold",
    "https://sencogoldanddiamonds.com/jewellery/category/modern-fancy-bracelet-gold",
    "https://sencogoldanddiamonds.com/jewellery/category/modern-fancy-bracelet-diamond",
    "https://sencogoldanddiamonds.com/jewellery/category/shell-pendant-gold",
    "https://sencogoldanddiamonds.com/jewellery/category/fancy-pendant-gold",
    "https://sencogoldanddiamonds.com/jewellery/category/modern-fancy-chains-gold",
    "https://sencogoldanddiamonds.com/jewellery/category/fancy-pendant-diamond",
    "https://sencogoldanddiamonds.com/jewellery/category/coin",
    "https://sencogoldanddiamonds.com/jewellery/category/bar",
    "https://sencogoldanddiamonds.com/jewellery/category/casual-nosepin-diamond",
    "https://sencogoldanddiamonds.com/jewellery/category/kaan",
    "https://sencogoldanddiamonds.com/jewellery/category/pendant-set",
    "https://sencogoldanddiamonds.com/jewellery/category/braceletdiamond",
    "https://sencogoldanddiamonds.com/jewellery/category/bracelet-platinum",
    "https://sencogoldanddiamonds.com/jewellery/category/platinum-bangle",
    "https://sencogoldanddiamonds.com/jewellery/category/platinum-churi",
    "https://sencogoldanddiamonds.com/jewellery/category/platinum-chains",
    "https://sencogoldanddiamonds.com/jewellery/category/platinum-fancy-chains",
    "https://sencogoldanddiamonds.com/jewellery/category/platinum-ring",
    "https://sencogoldanddiamonds.com/jewellery/category/platinum-engagement-ring",
    "https://sencogoldanddiamonds.com/jewellery/category/platinum-cocktail-ring",
    "https://sencogoldanddiamonds.com/jewellery/category/platinum-earring",
    "https://sencogoldanddiamonds.com/jewellery/category/platinum-stud-earring",
    "https://sencogoldanddiamonds.com/jewellery/category/platinum-drop-earring",
    "https://sencogoldanddiamonds.com/jewellery/category/platinum-necklace",
    "https://sencogoldanddiamonds.com/jewellery/category/platinum-pendants",
    "https://sencogoldanddiamonds.com/jewellery/category/platinum-fancy-pendant",
    "https://sencogoldanddiamonds.com/jewellery/category/coin-pendant",
    "https://sencogoldanddiamonds.com/jewellery/category/designer-pens",
    "https://sencogoldanddiamonds.com/jewellery/category/gold-utensils",
    "https://sencogoldanddiamonds.com/jewellery/category/silver-utensils",
    "https://sencogoldanddiamonds.com/jewellery/category/gents-astro-based-ring",
    "https://sencogoldanddiamonds.com/jewellery/category/ladies-astro-based-ring",
    "https://sencogoldanddiamonds.com/jewellery/category/engagement-ring-gold",
    "https://sencogoldanddiamonds.com/jewellery/category/spiral-ring-gold",
    "https://sencogoldanddiamonds.com/jewellery/category/boat-ring",
    "https://sencogoldanddiamonds.com/jewellery/category/umbrella-ring-gold",
    "https://sencogoldanddiamonds.com/jewellery/category/nailpolish-ring-gold",
    "https://sencogoldanddiamonds.com/jewellery/category/baby-ring-gold",
    "https://sencogoldanddiamonds.com/jewellery/category/makri-earrings-gold",
    "https://sencogoldanddiamonds.com/jewellery/category/baby-earrings-gold",
    "https://sencogoldanddiamonds.com/jewellery/category/god-pendant-gold",
    "https://sencogoldanddiamonds.com/jewellery/category/baby-pendant-gold",
    "https://sencogoldanddiamonds.com/jewellery/category/handmade-chain-gold",
    "https://sencogoldanddiamonds.com/jewellery/category/machine-made-chain-gold",
    "https://sencogoldanddiamonds.com/jewellery/category/tienecklace-gold",
    "https://sencogoldanddiamonds.com/jewellery/category/choker-necklace-gold",
    "https://sencogoldanddiamonds.com/jewellery/category/sleek-necklace-gold",
    "https://sencogoldanddiamonds.com/jewellery/category/lahari-necklace-gold",
    "https://sencogoldanddiamonds.com/jewellery/category/necklace-set-gold",
    "https://sencogoldanddiamonds.com/jewellery/category/kankan-bala-gold",
    "https://sencogoldanddiamonds.com/jewellery/category/churi-gold",
    "https://sencogoldanddiamonds.com/jewellery/category/ratan-chur-gold",
    "https://sencogoldanddiamonds.com/jewellery/category/charmslet-gold",
    "https://sencogoldanddiamonds.com/jewellery/category/engagement-ring-diamond",
    "https://sencogoldanddiamonds.com/jewellery/category/fancy-necklace-platinum",
    "https://sencogoldanddiamonds.com/jewellery/category/chain-pendant-platinum",
    "https://sencogoldanddiamonds.com/jewellery/category/sleek-necklace-platinum",
    "https://sencogoldanddiamonds.com/jewellery/category/double-chain-platinum",
    "https://sencogoldanddiamonds.com/jewellery/category/charmslet-platinum",
    "https://sencogoldanddiamonds.com/jewellery/category/platinum-wristlet",
    "https://sencogoldanddiamonds.com/jewellery/category/fancy-bracelet-platinum",
    "https://sencogoldanddiamonds.com/jewellery/category/fancy-necklace-gold",
    "https://sencogoldanddiamonds.com/jewellery/category/double-loop-pendant-gold",
    "https://sencogoldanddiamonds.com/jewellery/category/mens-ring-gold",
    "https://sencogoldanddiamonds.com/jewellery/category/polki-necklace",
    "https://sencogoldanddiamonds.com/jewellery/category/baby-pendant-diamond",
    "https://sencogoldanddiamonds.com/jewellery/category/god-pendant-diamond",
    "https://sencogoldanddiamonds.com/jewellery/category/baby-earrings-diamond",
    "https://sencogoldanddiamonds.com/jewellery/category/wristlet-diamond",
    "https://sencogoldanddiamonds.com/jewellery/category/fancy-nosepin-diamond",
    "https://sencogoldanddiamonds.com/jewellery/category/gold-nosepin",
    "https://sencogoldanddiamonds.com/jewellery/category/gold-nath",
    "https://sencogoldanddiamonds.com/jewellery/category/gold-bajubandh",
    "https://sencogoldanddiamonds.com/jewellery/category/mangalsutra-diamond",
    "https://sencogoldanddiamonds.com/jewellery/category/alphabet-pendant",
    "https://sencogoldanddiamonds.com/jewellery/category/green-pola",
    "https://sencogoldanddiamonds.com/jewellery/category/bengali-wedding",
    "https://sencogoldanddiamonds.com/jewellery/category/north-indian-wedding",
    "https://sencogoldanddiamonds.com/jewellery/category/bihari-wedding",
    "https://sencogoldanddiamonds.com/jewellery/category/kannada-wedding",
    "https://sencogoldanddiamonds.com/jewellery/category/telegu-wedding",
    "https://sencogoldanddiamonds.com/jewellery/category/muslim-wedding",
    "https://sencogoldanddiamonds.com/jewellery/category/upto-6-lac",
    "https://sencogoldanddiamonds.com/jewellery/category/upto-12-lac",
    "https://sencogoldanddiamonds.com/jewellery/category/upto-5-lac",
    "https://sencogoldanddiamonds.com/jewellery/category/upto-9-lac",
    "https://sencogoldanddiamonds.com/jewellery/category/diamond-bangle",
    "https://sencogoldanddiamonds.com/jewellery/category/diamond-pola",
    "https://sencogoldanddiamonds.com/jewellery/category/diamond-noa",
    "https://sencogoldanddiamonds.com/jewellery/category/baby-chain",
    "https://sencogoldanddiamonds.com/jewellery/category/churi-diamond",
    "https://sencogoldanddiamonds.com/jewellery/category/tushi-necklace",
    "https://sencogoldanddiamonds.com/jewellery/category/mens-ring-diamond",
    "https://sencogoldanddiamonds.com/jewellery/category/bracelet-customer-favourite",
    "https://sencogoldanddiamonds.com/jewellery/category/earrings-customer-favourite",
    "https://sencogoldanddiamonds.com/jewellery/category/necklace-customer-favourite",
    "https://sencogoldanddiamonds.com/jewellery/category/nosepin-customer-favourite",
    "https://sencogoldanddiamonds.com/jewellery/category/pendant-customer-favourite",
    "https://sencogoldanddiamonds.com/jewellery/category/pendant-set-customer-favourite",
    "https://sencogoldanddiamonds.com/jewellery/category/accessories-all-products",
    "https://sencogoldanddiamonds.com/jewellery/category/bangle-all-products",
    "https://sencogoldanddiamonds.com/jewellery/category/bracelet-all-products",
    "https://sencogoldanddiamonds.com/jewellery/category/chain-all-products",
    "https://sencogoldanddiamonds.com/jewellery/category/earrings-all-products",
    "https://sencogoldanddiamonds.com/jewellery/category/mangalsutra-all-products",
    "https://sencogoldanddiamonds.com/jewellery/category/necklace-all-products",
    "https://sencogoldanddiamonds.com/jewellery/category/nosepin-all-products",
    "https://sencogoldanddiamonds.com/jewellery/category/pendant-all-products",
    "https://sencogoldanddiamonds.com/jewellery/category/pendant-set-all-products",
    "https://sencogoldanddiamonds.com/jewellery/category/ring-all-products",
    "https://sencogoldanddiamonds.com/jewellery/category/wristlet-all-products",
    "https://sencogoldanddiamonds.com/jewellery/category/party-necklace-diamond",
    "https://sencogoldanddiamonds.com/jewellery/category/wedding-necklace-diamond",
    "https://sencogoldanddiamonds.com/jewellery/category/gifts-under-10k-pendant",
    "https://sencogoldanddiamonds.com/jewellery/category/gifts-under-10k-ring",
    "https://sencogoldanddiamonds.com/jewellery/category/gifts-under-10k-nosepin",
    "https://sencogoldanddiamonds.com/jewellery/category/gifts-under-10k-earrings",
    "https://sencogoldanddiamonds.com/jewellery/category/gifts-under-10k-bracelet",
    "https://sencogoldanddiamonds.com/jewellery/category/gifts-under-10k-bangle",
    "https://sencogoldanddiamonds.com/jewellery/category/gifts-for-her-pendant",
    "https://sencogoldanddiamonds.com/jewellery/category/gifts-for-her-earrings",
    "https://sencogoldanddiamonds.com/jewellery/category/gifts-for-her-nosepin",
    "https://sencogoldanddiamonds.com/jewellery/category/gifts-for-her-ring",
    "https://sencogoldanddiamonds.com/jewellery/category/gifts-for-her-bracelet",
    "https://sencogoldanddiamonds.com/jewellery/category/gifts-for-her-bangle",
    "https://sencogoldanddiamonds.com/jewellery/category/gifts-for-her-chain-pendant",
    "https://sencogoldanddiamonds.com/jewellery/category/gifts-for-her-jewellery-set",
    "https://sencogoldanddiamonds.com/jewellery/category/gifts-for-her-necklace",
    "https://sencogoldanddiamonds.com/jewellery/category/gifts-for-her-mangtika",
    "https://sencogoldanddiamonds.com/jewellery/category/gifts-for-him-pendant",
    "https://sencogoldanddiamonds.com/jewellery/category/gifts-for-him-accesories",
    "https://sencogoldanddiamonds.com/jewellery/category/gifts-for-him-ring",
    "https://sencogoldanddiamonds.com/jewellery/category/gifts-for-him-wristlet",
    "https://sencogoldanddiamonds.com/jewellery/category/gifts-for-him-chain",
    "https://sencogoldanddiamonds.com/jewellery/category/gift-solitaires-ring",
    "https://sencogoldanddiamonds.com/jewellery/category/gift-solitaires-earrings",
    "https://sencogoldanddiamonds.com/jewellery/category/gift-solitaires-pendant",
    "https://sencogoldanddiamonds.com/jewellery/category/gift-solitaires-nosepin",
    "https://sencogoldanddiamonds.com/jewellery/category/pola-necklace",
    "https://sencogoldanddiamonds.com/jewellery/category/bracelet-nova-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/chain-pendant-nova-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/earrings-nova-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/chain-aham-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/pendant-aham-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/accessories-aham-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/ring-aham-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/wristlet-aham-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/bangle-yatra-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/bracelet-yatra-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/earrings-yatra-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/necklace-yatra-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/pendant-yatra-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/pendant-set-yatra-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/ring-yatra-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/earrings-vintage-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/pendant-vintage-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/ring-vintage-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/earrings-signature-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/earrings-deccan-queen-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/bracelet-victoria-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/earrings-victoria-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/necklace-victoria-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/pendant-victoria-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/ring-victoria-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/pendant-mayurpankh-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/ring-mayurpankh-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/earrings-perfect-love-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/mangalsutra-perfect-love-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/nosepin-perfect-love-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/pendant-perfect-love-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/ring-perfect-love-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/bangle-evara-platinum",
    "https://sencogoldanddiamonds.com/jewellery/category/bracelet-evara-platinum",
    "https://sencogoldanddiamonds.com/jewellery/category/chain-evara-platinum",
    "https://sencogoldanddiamonds.com/jewellery/category/earrings-evara-platinum",
    "https://sencogoldanddiamonds.com/jewellery/category/necklace-evara-platinum",
    "https://sencogoldanddiamonds.com/jewellery/category/pendant-evara-platinum",
    "https://sencogoldanddiamonds.com/jewellery/category/ring-evara-platinum",
    "https://sencogoldanddiamonds.com/jewellery/category/earrings-love-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/pendant-love-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/ring-love-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/earrings-freedom-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/pendant-freedom-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/ring-freedom-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/pendant-aqua-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/ring-aqua-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/earrings-denim-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/pendant-denim-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/bracelet-daisy-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/pendant-daisy-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/ring-daisy-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/earrings-magnificience-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/pendant-magnificience-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/bracelet-ya-devi-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/earrings-ya-devi-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/pendant-ya-devi-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/ring-ya-devi-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/necklace-tribe-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/earrings-tribe-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/earrings-floral-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/pendant-floral-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/ring-floral-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/earrings-venus-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/pendant-venus-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/earrings-colors-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/pendant-colors-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/ring-colors-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/earrings-coconut-shell-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/pendant-set-coconut-shell-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/pendant-coconut-shell-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/accessories-kids-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/bangle-kids-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/earrings-kids-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/pendant-kids-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/ring-kids-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/bangle-bengali-wedding",
    "https://sencogoldanddiamonds.com/jewellery/category/earrings-bengali-wedding",
    "https://sencogoldanddiamonds.com/jewellery/category/necklace-bengali-wedding",
    "https://sencogoldanddiamonds.com/jewellery/category/nosepin-bengali-wedding",
    "https://sencogoldanddiamonds.com/jewellery/category/pendant-bengali-wedding",
    "https://sencogoldanddiamonds.com/jewellery/category/ring-bengali-wedding",
    "https://sencogoldanddiamonds.com/jewellery/category/bangle-north-indian-wedding",
    "https://sencogoldanddiamonds.com/jewellery/category/bracelet-north-indian-wedding",
    "https://sencogoldanddiamonds.com/jewellery/category/earrings-north-indian-wedding",
    "https://sencogoldanddiamonds.com/jewellery/category/necklace-north-indian-wedding",
    "https://sencogoldanddiamonds.com/jewellery/category/pendant-set-north-indian-wedding",
    "https://sencogoldanddiamonds.com/jewellery/category/pendant-north-indian-wedding",
    "https://sencogoldanddiamonds.com/jewellery/category/ring-north-indian-wedding",
    "https://sencogoldanddiamonds.com/jewellery/category/earrings-bihari-wedding",
    "https://sencogoldanddiamonds.com/jewellery/category/necklace-bihari-wedding",
    "https://sencogoldanddiamonds.com/jewellery/category/ring-bihari-wedding",
    "https://sencogoldanddiamonds.com/jewellery/category/bangle-kannada-wedding",
    "https://sencogoldanddiamonds.com/jewellery/category/earrings-kannada-wedding",
    "https://sencogoldanddiamonds.com/jewellery/category/necklace-kannada-wedding",
    "https://sencogoldanddiamonds.com/jewellery/category/bangle-telegu-wedding",
    "https://sencogoldanddiamonds.com/jewellery/category/earrings-telegu-wedding",
    "https://sencogoldanddiamonds.com/jewellery/category/necklace-telegu-wedding",
    "https://sencogoldanddiamonds.com/jewellery/category/earrings-muslim-wedding",
    "https://sencogoldanddiamonds.com/jewellery/category/necklace-muslim-wedding",
    "https://sencogoldanddiamonds.com/jewellery/category/ginkgo-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/pola-ring-gold",
    "https://sencogoldanddiamonds.com/jewellery/category/belt",
    "https://sencogoldanddiamonds.com/jewellery/category/brooch",
    "https://sencogoldanddiamonds.com/jewellery/category/button",
    "https://sencogoldanddiamonds.com/jewellery/category/cufflink-premium-accessories",
    "https://sencogoldanddiamonds.com/jewellery/category/tie-pin",
    "https://sencogoldanddiamonds.com/jewellery/category/spoon",
    "https://sencogoldanddiamonds.com/jewellery/category/bowl",
    "https://sencogoldanddiamonds.com/jewellery/category/glass",
    "https://sencogoldanddiamonds.com/jewellery/category/plate",
    "https://sencogoldanddiamonds.com/jewellery/category/cup",
    "https://sencogoldanddiamonds.com/jewellery/category/kalash",
    "https://sencogoldanddiamonds.com/jewellery/category/idol",
    "https://sencogoldanddiamonds.com/jewellery/category/mangaldeep",
    "https://sencogoldanddiamonds.com/jewellery/category/diya",
    "https://sencogoldanddiamonds.com/jewellery/category/kajal-lota",
    "https://sencogoldanddiamonds.com/jewellery/category/sindoor-dani",
    "https://sencogoldanddiamonds.com/jewellery/category/throne",
    "https://sencogoldanddiamonds.com/jewellery/category/sruti-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/mangalsutras-gold",
    "https://sencogoldanddiamonds.com/jewellery/category/bangle-utsav-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/evil-eye-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/22kt-jewellery",
    "https://sencogoldanddiamonds.com/jewellery/category/mariposa-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/cera-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/spectra-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/shakti-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/lotus-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/power-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/ganesh-chaturthi-special",
    "https://sencogoldanddiamonds.com/jewellery/category/earrings-festival",
    "https://sencogoldanddiamonds.com/jewellery/category/diamond-chain",
    "https://sencogoldanddiamonds.com/jewellery/category/puja-utensils",
    "https://sencogoldanddiamonds.com/jewellery/category/bala-bangle-utsav-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/churi-bangle-utsav-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/bracelet-bangle-utsav-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/mens-wristlet-bangle-utsav-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/noa-bangle-utsav-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/charmslet-bangle-utsav-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/sankha-bangle-utsav-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/pola-bangle-utsav-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/chur-bangle-utsav-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/mens-ring-platinum",
    "https://sencogoldanddiamonds.com/jewellery/category/satya-prem-ki-katha",
    "https://sencogoldanddiamonds.com/jewellery/category/gold-chain-pendant",
    "https://sencogoldanddiamonds.com/jewellery/category/alphabet-pendant-diamond",
    "https://sencogoldanddiamonds.com/jewellery/category/mangalsutra-customer-favourite",
    "https://sencogoldanddiamonds.com/jewellery/category/lord-ganesh",
    "https://sencogoldanddiamonds.com/jewellery/category/goddess-laxmi",
    "https://sencogoldanddiamonds.com/jewellery/category/laxmi-ganesh",
    "https://sencogoldanddiamonds.com/jewellery/category/laxmi-narayan",
    "https://sencogoldanddiamonds.com/jewellery/category/bal-gopal",
    "https://sencogoldanddiamonds.com/jewellery/category/signature-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/bracelet-tribe-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/pendant-tribe-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/earrings-mariposa-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/necklace-mariposa-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/ring-mariposa-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/chain-pendant-mariposa-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/bracelet-mariposa-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/ring-venus-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/bracelet-venus-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/bracelet-denim-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/chain-pendant-denim-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/necklace-love-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/bracelet-love-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/chain-pendant-love-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/ring-ginkgo-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/earrings-ginkgo-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/pendant-ginkgo-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/bracelet-ginkgo-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/necklace-ginkgo-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/necklace-tria-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/earrings-tria-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/earrings-tropica-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/pendant-tropica-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/ring-tropica-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/necklace-tropica-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/chain-pendant-tropica-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/pendant-love-2023",
    "https://sencogoldanddiamonds.com/jewellery/category/earrings-love-2023",
    "https://sencogoldanddiamonds.com/jewellery/category/ring-love-2023",
    "https://sencogoldanddiamonds.com/jewellery/category/chain-pendant-love-2023",
    "https://sencogoldanddiamonds.com/jewellery/category/ring-cera-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/earrings-cera-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/pendant-cera-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/earrings-evil-eye-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/pendant-evil-eye-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/ring-evil-eye-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/bracelet-evil-eye-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/chain-pendant-evil-eye-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/earrings-spectra-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/necklace-spectra-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/ring-spectra-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/chain-pendant-spectra-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/bracelet-spectra-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/earrings-lotus-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/pendant-lotus-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/ring-lotus-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/chain-pendant-lotus-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/earrings-power-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/pendant-power-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/ring-power-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/pendant-shakti-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/earrings-shakti-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/ring-shakti-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/necklace-shakti-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/bracelet-shakti-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/chain-pendant-shakti-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/mangalsutra-signature-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/chain-pendant-signature-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/ring-signature-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/necklace-shagun-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/earrings-shagun-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/ring-shagun-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/bangle-shagun-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/bracelet-shagun-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/necklace-radwada-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/earrings-rajwada-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/ring-rajwada-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/bangle-rajwada-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/bracelet-rajwada-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/sankha-bangle-rajwada-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/pola-bangle-rajwada-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/necklace-satyaprem-ki-katha",
    "https://sencogoldanddiamonds.com/jewellery/category/earrings-satyaprem-ki-katha",
    "https://sencogoldanddiamonds.com/jewellery/category/bangle-satyaprem-ki-katha",
    "https://sencogoldanddiamonds.com/jewellery/category/necklace-milon-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/earrings-milon-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/ring-milon-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/pendant-spectra-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/pendant-mariposa-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/bangle-mariposa-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/necklace-rajwada-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/mangtika-rajwada-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/hermosa-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/diamond-hoop-earrings",
    "https://sencogoldanddiamonds.com/jewellery/category/bangle-everlite-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/bracelet-everlite-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/chain-everlite-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/chain-pendant-everlite-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/earrings-everlite-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/mangalsutra-everlite-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/necklace-everlite-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/nose-pin-everlite-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/pendant-everlite-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/pendant-set-everlite-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/ring-everlite-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/wristlet-everlite-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/earrings-hermosa-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/pendant-hermosa-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/earrings-sruti-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/siyaram-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/necklace-siyaram-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/pendant-siyaram-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/chain-pendant-siyaram-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/earrings-siyaram-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/festival-of-love",
    "https://sencogoldanddiamonds.com/jewellery/category/chain-pendant-tria-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/ring-tria-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/romantique-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/love-2024",
    "https://sencogoldanddiamonds.com/jewellery/category/bangle-siyaram-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/earrings-romantique-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/necklace-romantique-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/bracelet-love-2024",
    "https://sencogoldanddiamonds.com/jewellery/category/chain-pendant-love-2024",
    "https://sencogoldanddiamonds.com/jewellery/category/earrings-love-2024",
    "https://sencogoldanddiamonds.com/jewellery/category/pendant-love-2024",
    "https://sencogoldanddiamonds.com/jewellery/category/ring-love-2024",
    "https://sencogoldanddiamonds.com/jewellery/category/men-gold-chain",
    "https://sencogoldanddiamonds.com/jewellery/category/women-gold-chain",
    "https://sencogoldanddiamonds.com/jewellery/category/unisex-gold-chain",
    "https://sencogoldanddiamonds.com/jewellery/category/men-platinum-chain",
    "https://sencogoldanddiamonds.com/jewellery/category/women-platinum-chain",
    "https://sencogoldanddiamonds.com/jewellery/category/unisex-platinum-chain",
    "https://sencogoldanddiamonds.com/jewellery/category/men-diamond-chain",
    "https://sencogoldanddiamonds.com/jewellery/category/unisex-diamond-chain",
    "https://sencogoldanddiamonds.com/jewellery/category/ribbon-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/bracelet-ribbon-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/bangle-ribbon-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/chain-pendant-ribbon-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/earrings-ribbon-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/ring-ribbon-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/terracotta-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/pendant-terracotta-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/earrings-terracotta-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/ring-terracotta-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/modern-gold-mangalsutra",
    "https://sencogoldanddiamonds.com/jewellery/category/traditional-gold-mangalsutra",
    "https://sencogoldanddiamonds.com/jewellery/category/floral-gold-mangalsutra",
    "https://sencogoldanddiamonds.com/jewellery/category/eid-special",
    "https://sencogoldanddiamonds.com/jewellery/category/modern-diamond-mangalsutra",
    "https://sencogoldanddiamonds.com/jewellery/category/traditional-diamond-mangalsutra",
    "https://sencogoldanddiamonds.com/jewellery/category/solitaire-diamond-mangalsutra",
    "https://sencogoldanddiamonds.com/jewellery/category/floral-diamond-mangalsutra",
    "https://sencogoldanddiamonds.com/jewellery/category/diamond-solitaire-earrings",
    "https://sencogoldanddiamonds.com/jewellery/category/diamond-solitaire-rings",
    "https://sencogoldanddiamonds.com/jewellery/category/diamond-solitaire-pendants",
    "https://sencogoldanddiamonds.com/jewellery/category/gathbandhan-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/bangle-gathbandhan-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/earrings-gathbandhan-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/necklace-gathbandhan-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/ring-gathbandhan-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/wristlet-gathbandhan-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/pleat-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/earrings-pleat-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/ring-pleat-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/pendant-pleat-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/bracelet-pleat-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/chain-pendant-pleat-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/mens-pendant-diamond",
    "https://sencogoldanddiamonds.com/jewellery/category/mens-pendant-gold",
    "https://sencogoldanddiamonds.com/jewellery/category/kada-aham-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/gold-maang-tikka",
    "https://sencogoldanddiamonds.com/jewellery/category/queen-bee-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/pendant-queen-bee-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/bracelet-queen-bee-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/ring-queen-bee-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/earring-queen-bee-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/mens-kada-platinum",
    "https://sencogoldanddiamonds.com/jewellery/category/chain-festival",
    "https://sencogoldanddiamonds.com/jewellery/category/chain-pendant-diamond",
    "https://sencogoldanddiamonds.com/jewellery/category/women-jewellery",
    "https://sencogoldanddiamonds.com/jewellery/category/chain-pendant-all-products",
    "https://sencogoldanddiamonds.com/jewellery/category/beans",
    "https://sencogoldanddiamonds.com/jewellery/category/god-pendant-platinum",
    "https://sencogoldanddiamonds.com/jewellery/category/aparupa-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/earrings-for-women",
    "https://sencogoldanddiamonds.com/jewellery/category/pendant-for-women",
    "https://sencogoldanddiamonds.com/jewellery/category/necklace-for-women",
    "https://sencogoldanddiamonds.com/jewellery/category/chain-pendant-for-women",
    "https://sencogoldanddiamonds.com/jewellery/category/ring-for-women",
    "https://sencogoldanddiamonds.com/jewellery/category/bracelets-for-women",
    "https://sencogoldanddiamonds.com/jewellery/category/bangle-for-women",
    "https://sencogoldanddiamonds.com/jewellery/category/chain-for-women",
    "https://sencogoldanddiamonds.com/jewellery/category/mangalsutra-for-women",
    "https://sencogoldanddiamonds.com/jewellery/category/maang-tikka",
    "https://sencogoldanddiamonds.com/jewellery/category/nose-pin-for-women",
    "https://sencogoldanddiamonds.com/jewellery/category/nath",
    "https://sencogoldanddiamonds.com/jewellery/category/bracelets-lotus-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/pendant-shagun-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/regalia-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/gold-coins-bars-and-beans",
    "https://sencogoldanddiamonds.com/jewellery/category/silver-coins-and-bars",
    "https://sencogoldanddiamonds.com/jewellery/category/vivaah-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/diamond-men's-earrings",
    "https://sencogoldanddiamonds.com/jewellery/category/zodiac-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/ring-and-earrings-all-products",
    "https://sencogoldanddiamonds.com/jewellery/category/chain-and-mangalsutra",
    "https://sencogoldanddiamonds.com/jewellery/category/vivaah-collection-necklace",
    "https://sencogoldanddiamonds.com/jewellery/category/vivaah-collection-earrings",
    "https://sencogoldanddiamonds.com/jewellery/category/vivaah-collection-ring",
    "https://sencogoldanddiamonds.com/jewellery/category/vivaah-collection-maang-tikka",
    "https://sencogoldanddiamonds.com/jewellery/category/vivaah-collection-bracelet",
    "https://sencogoldanddiamonds.com/jewellery/category/expressions-of-love",
    "https://sencogoldanddiamonds.com/jewellery/category/berry-lovely-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/facets-of-love-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/ice-cube-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/valentines-special-diamond-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/rose-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/ombre-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/silver-products",
    "https://sencogoldanddiamonds.com/jewellery/category/polki-all-products",
    "https://sencogoldanddiamonds.com/jewellery/category/watch",
    "https://sencogoldanddiamonds.com/jewellery/category/aham-platinum",
    "https://sencogoldanddiamonds.com/jewellery/category/infinity-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/lord-hanuman",
    "https://sencogoldanddiamonds.com/jewellery/category/golden-curve-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/golden-curve-collection-earrings",
    "https://sencogoldanddiamonds.com/jewellery/category/golden-curve-collection-necklace",
    "https://sencogoldanddiamonds.com/jewellery/category/golden-curve-collection-pendant",
    "https://sencogoldanddiamonds.com/jewellery/category/vivaah-collection-bangle",
    "https://sencogoldanddiamonds.com/jewellery/category/vivaah-collection-chain",
    "https://sencogoldanddiamonds.com/jewellery/category/ombre-collection-earrings",
    "https://sencogoldanddiamonds.com/jewellery/category/ombre-collection-rings",
    "https://sencogoldanddiamonds.com/jewellery/category/ombre-collection-pendant",
    "https://sencogoldanddiamonds.com/jewellery/category/ombre-collection-bracelet",
    "https://sencogoldanddiamonds.com/jewellery/category/infinity-collection-earrings",
    "https://sencogoldanddiamonds.com/jewellery/category/infinity-collection-chain-pendant",
    "https://sencogoldanddiamonds.com/jewellery/category/facets-of-love-collection-rings",
    "https://sencogoldanddiamonds.com/jewellery/category/facets-of-love-collection-earrings",
    "https://sencogoldanddiamonds.com/jewellery/category/facets-of-love-collection-pendant",
    "https://sencogoldanddiamonds.com/jewellery/category/nayiraah-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/nayiraah-collection-necklace",
    "https://sencogoldanddiamonds.com/jewellery/category/nayiraah-collection-earrings",
    "https://sencogoldanddiamonds.com/jewellery/category/berry-lovely-collection-earrings",
    "https://sencogoldanddiamonds.com/jewellery/category/berry-lovely-collection-necklace",
    "https://sencogoldanddiamonds.com/jewellery/category/berry-lovely-collection-rings",
    "https://sencogoldanddiamonds.com/jewellery/category/valentine's-special-diamond-collection-bracelet",
    "https://sencogoldanddiamonds.com/jewellery/category/valentine's-special-diamond-collection-bangle",
    "https://sencogoldanddiamonds.com/jewellery/category/valentine's-special-diamond-collection-rings",
    "https://sencogoldanddiamonds.com/jewellery/category/valentine's-special-diamond-collection-wristlet",
    "https://sencogoldanddiamonds.com/jewellery/category/valentine's-special-diamond-collection-pendant",
    "https://sencogoldanddiamonds.com/jewellery/category/valentine's-special-diamond-collection-earrings",
    "https://sencogoldanddiamonds.com/jewellery/category/valentine's-special-diamond-collection-necklace",
    "https://sencogoldanddiamonds.com/jewellery/category/rose-collection-bracelet",
    "https://sencogoldanddiamonds.com/jewellery/category/rose-collection-earrings",
    "https://sencogoldanddiamonds.com/jewellery/category/rose-collection-rings",
    "https://sencogoldanddiamonds.com/jewellery/category/rose-collection-chain-pendant",
    "https://sencogoldanddiamonds.com/jewellery/category/ice-cube-collection-rings",
    "https://sencogoldanddiamonds.com/jewellery/category/ice-cube-collection-pendant",
    "https://sencogoldanddiamonds.com/jewellery/category/ice-cube-collection-earrings",
    "https://sencogoldanddiamonds.com/jewellery/category/daily-wear-diamond-earrings",
    "https://sencogoldanddiamonds.com/jewellery/category/daily-wear-gold-earrings",
    "https://sencogoldanddiamonds.com/jewellery/category/simple-gold-necklace",
    "https://sencogoldanddiamonds.com/jewellery/category/simple-diamond-necklace",
    "https://sencogoldanddiamonds.com/jewellery/category/simple-diamond-ring",
    "https://sencogoldanddiamonds.com/jewellery/category/3-gram-gold-earrings",
    "https://sencogoldanddiamonds.com/jewellery/category/light-weight-gold-earrings",
    "https://sencogoldanddiamonds.com/jewellery/category/antique-gold-necklace",
    "https://sencogoldanddiamonds.com/jewellery/category/gold-earcuffs",
    "https://sencogoldanddiamonds.com/jewellery/category/gold-kada-for-women",
    "https://sencogoldanddiamonds.com/jewellery/category/gold-rings-for-couple",
    "https://sencogoldanddiamonds.com/jewellery/category/sui-dhaga-earrings",
    "https://sencogoldanddiamonds.com/jewellery/category/rose-gold-earring",
    "https://sencogoldanddiamonds.com/jewellery/category/kundan-earrings",
    "https://sencogoldanddiamonds.com/jewellery/category/one-gram-gold-earrings",
    "https://sencogoldanddiamonds.com/jewellery/category/rakhi-all-products",
    "https://sencogoldanddiamonds.com/jewellery/category/rakhi-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/raksha-bandhan-bracelet-pendant",
    "https://sencogoldanddiamonds.com/jewellery/category/teej-jewellery",
    "https://sencogoldanddiamonds.com/jewellery/category/0.5-gm-gold-coin",
    "https://sencogoldanddiamonds.com/jewellery/category/1-gm-gold-coin",
    "https://sencogoldanddiamonds.com/jewellery/category/2-gm-gold-coin",
    "https://sencogoldanddiamonds.com/jewellery/category/5-gm-gold-coin",
    "https://sencogoldanddiamonds.com/jewellery/category/10-gm-gold-coin",
    "https://sencogoldanddiamonds.com/jewellery/category/20-gm-gold-coin",
    "https://sencogoldanddiamonds.com/jewellery/category/50-gm-silver-coin",
    "https://sencogoldanddiamonds.com/jewellery/category/100-gm-silver-coin",
    "https://sencogoldanddiamonds.com/jewellery/category/500-gm-silver-coin",
    "https://sencogoldanddiamonds.com/jewellery/category/varalaxmi-collections",
    "https://sencogoldanddiamonds.com/jewellery/category/elements-of-nature",
    "https://sencogoldanddiamonds.com/jewellery/category/man-of-platinum",
    "https://sencogoldanddiamonds.com/jewellery/category/9kt-jewellery",
    "https://sencogoldanddiamonds.com/jewellery/category/18kt-jewellery",
    "https://sencogoldanddiamonds.com/jewellery/category/14kt-jewellery",
    "https://sencogoldanddiamonds.com/jewellery/category/princess-cut-diamond-engagement-ring",
    "https://sencogoldanddiamonds.com/jewellery/category/heart-shaped-diamond-ring",
    "https://sencogoldanddiamonds.com/jewellery/category/oval-diamond-ring",
    "https://sencogoldanddiamonds.com/jewellery/category/square-diamond-ring",
    "https://sencogoldanddiamonds.com/jewellery/category/princess-cut-engagement-ring",
    "https://sencogoldanddiamonds.com/jewellery/category/oval-engagement-ring",
    "https://sencogoldanddiamonds.com/jewellery/category/round-cut-engagement-rings",
    "https://sencogoldanddiamonds.com/jewellery/category/round-engagement-ring",
    "https://sencogoldanddiamonds.com/jewellery/category/pear-shape-diamond-ring",
    "https://sencogoldanddiamonds.com/jewellery/category/pear-diamond-engagement-ring",
    "https://sencogoldanddiamonds.com/jewellery/category/cushion-cut-diamond-ring",
    "https://sencogoldanddiamonds.com/jewellery/category/cushion-cut-diamond-engagement-rings",
    "https://sencogoldanddiamonds.com/jewellery/category/silver-jewellery",
    "https://sencogoldanddiamonds.com/jewellery/category/silver-jewellery-men",
    "https://sencogoldanddiamonds.com/jewellery/category/silver-jewellery-women",
    "https://sencogoldanddiamonds.com/jewellery/category/silver-bracelet-women",
    "https://sencogoldanddiamonds.com/jewellery/category/silver-rings-women",
    "https://sencogoldanddiamonds.com/jewellery/category/silver-earrings-women",
    "https://sencogoldanddiamonds.com/jewellery/category/silver-chain-mens",
    "https://sencogoldanddiamonds.com/jewellery/category/silver-anklets",
    "https://sencogoldanddiamonds.com/jewellery/category/mens-silver-ring",
    "https://sencogoldanddiamonds.com/jewellery/category/ganesha-pendant-gold",
    "https://sencogoldanddiamonds.com/jewellery/category/rose-gold-jewellery",
    "https://sencogoldanddiamonds.com/jewellery/category/gold-studs-men",
    "https://sencogoldanddiamonds.com/jewellery/category/diamond-mens-earrings",
    "https://sencogoldanddiamonds.com/jewellery/category/navratri-durga-puja-jewellery",
    "https://sencogoldanddiamonds.com/jewellery/category/onam-jewellery",
    "https://sencogoldanddiamonds.com/jewellery/category/ganesh-locket-gold",
    "https://sencogoldanddiamonds.com/jewellery/category/teachers-day-gift",
    "https://sencogoldanddiamonds.com/jewellery/category/diwali-gift-ideas",
    "https://sencogoldanddiamonds.com/jewellery/category/akshaya-tritiya-gold-offers",
    "https://sencogoldanddiamonds.com/jewellery/category/diwali-jewellery",
    "https://sencogoldanddiamonds.com/jewellery/category/silver-bowl",
    "https://sencogoldanddiamonds.com/jewellery/category/bowl-gold",
    "https://sencogoldanddiamonds.com/jewellery/category/cup-silver",
    "https://sencogoldanddiamonds.com/jewellery/category/diya-silver",
    "https://sencogoldanddiamonds.com/jewellery/category/diya-stand-silver",
    "https://sencogoldanddiamonds.com/jewellery/category/glass-silver",
    "https://sencogoldanddiamonds.com/jewellery/category/kalash-silver",
    "https://sencogoldanddiamonds.com/jewellery/category/mukut-silver",
    "https://sencogoldanddiamonds.com/jewellery/category/plate-silver",
    "https://sencogoldanddiamonds.com/jewellery/category/pooja-jhula-silver",
    "https://sencogoldanddiamonds.com/jewellery/category/sindoor-dani-silver",
    "https://sencogoldanddiamonds.com/jewellery/category/spoon-silver",
    "https://sencogoldanddiamonds.com/jewellery/category/spoon-gold",
    "https://sencogoldanddiamonds.com/jewellery/category/utensils-silver",
    "https://sencogoldanddiamonds.com/jewellery/category/utensils-gold",
    "https://sencogoldanddiamonds.com/jewellery/category/heart-shaped-engagement-ring",
    "https://sencogoldanddiamonds.com/jewellery/category/diamond-button",
    "https://sencogoldanddiamonds.com/jewellery/category/diamond-cufflink",
    "https://sencogoldanddiamonds.com/jewellery/category/diamond-tie-pin",
    "https://sencogoldanddiamonds.com/jewellery/category/gold-brooch",
    "https://sencogoldanddiamonds.com/jewellery/category/gold-buckle",
    "https://sencogoldanddiamonds.com/jewellery/category/gold-cufflink",
    "https://sencogoldanddiamonds.com/jewellery/category/gold-tie-pin",
    "https://sencogoldanddiamonds.com/jewellery/category/platinum-watch",
    "https://sencogoldanddiamonds.com/jewellery/category/silver-mall",
    "https://sencogoldanddiamonds.com/jewellery/category/premium-accessories-diamond",
    "https://sencogoldanddiamonds.com/jewellery/category/premium-accessories-gold",
    "https://sencogoldanddiamonds.com/jewellery/category/premium-accessories-platinum",
    "https://sencogoldanddiamonds.com/jewellery/category/premium-accessories-silver",
    "https://sencogoldanddiamonds.com/jewellery/category/durga-puja-navratri-jewellery",
    "https://sencogoldanddiamonds.com/jewellery/category/cloud9-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/elements-of-love",
    "https://sencogoldanddiamonds.com/jewellery/category/2-gram-gold-earrings",
    "https://sencogoldanddiamonds.com/jewellery/category/4-gram-gold-earrings",
    "https://sencogoldanddiamonds.com/jewellery/category/5-gram-gold-earrings",
    "https://sencogoldanddiamonds.com/jewellery/category/10-gram-gold-jhumka",
    "https://sencogoldanddiamonds.com/jewellery/category/5-gram-gold-jhumka",
    "https://sencogoldanddiamonds.com/jewellery/category/10-gram-gold-mangalsutra",
    "https://sencogoldanddiamonds.com/jewellery/category/20-gram-gold-mangalsutra",
    "https://sencogoldanddiamonds.com/jewellery/category/valentines-day-gifts",
    "https://sencogoldanddiamonds.com/jewellery/category/valentines-day-gifts-for-him",
    "https://sencogoldanddiamonds.com/jewellery/category/valentines-day-gifts-for-her",
    "https://sencogoldanddiamonds.com/jewellery/category/valentines-day-gifts-for-boyfriend",
    "https://sencogoldanddiamonds.com/jewellery/category/valentines-day-gifts-for-girlfriend",
    "https://sencogoldanddiamonds.com/jewellery/category/jiostar-special",
    "https://sencogoldanddiamonds.com/jewellery/category/a-initial-gold-pendant",
    "https://sencogoldanddiamonds.com/jewellery/category/s-initial-gold-pendant",
    "https://sencogoldanddiamonds.com/jewellery/category/5-gram-gold-chain",
    "https://sencogoldanddiamonds.com/jewellery/category/7-gram-gold-chain",
    "https://sencogoldanddiamonds.com/jewellery/category/6-gram-gold-chain",
    "https://sencogoldanddiamonds.com/jewellery/category/8-gram-gold-chain",
    "https://sencogoldanddiamonds.com/jewellery/category/versa-collection",
    "https://sencogoldanddiamonds.com/jewellery/category/earrings-for-haldi",
    "https://sencogoldanddiamonds.com/jewellery/category/haldi-maang-tika",
    "https://sencogoldanddiamonds.com/jewellery/category/necklace-for-haldi",
    "https://sencogoldanddiamonds.com/jewellery/category/haldi-bangles",
    "https://sencogoldanddiamonds.com/jewellery/category/bridal-earrings",
    "https://sencogoldanddiamonds.com/jewellery/category/heavy-gold-earrings-for-wedding",
    "https://sencogoldanddiamonds.com/jewellery/category/light-weight-gold-jewellery",
    "https://sencogoldanddiamonds.com/jewellery/category/light-weight-gold-chain",
    "https://sencogoldanddiamonds.com/jewellery/category/light-weight-gold-necklace",
    "https://sencogoldanddiamonds.com/jewellery/category/light-weight-gold-bangle",
    "https://sencogoldanddiamonds.com/jewellery/category/light-weight-mangalsutra",
    "https://sencogoldanddiamonds.com/jewellery/category/light-weight-gold-pendant",
    "https://sencogoldanddiamonds.com/jewellery/category/bangle-utsav2026",
    "https://sencogoldanddiamonds.com/jewellery/category/chur-bangle-platinum",
    "https://sencogoldanddiamonds.com/jewellery/category/silver-all-products"
]

# ==========================================
# 🛑 PHASE 1: DYNAMIC CATEGORY HARVESTER
# ==========================================
async def harvest_category_keywords(session, url, categories_set, semaphore):
    async with semaphore:
        try:
            response = await session.get(url, impersonate="chrome120", timeout=15)
            if response.status_code != 200:
                return

            # Fallback: Agar filter nahi mila, toh URL se hi slug nikal lo
            fallback_cat = url.split('/')[-1].replace('-', ' ').strip().lower()
            if fallback_cat:
                categories_set.add(fallback_cat)

            tree = HTMLParser(response.text)
            
            # CSS Selector tumhare screenshot ke hisaab se
            filter_items = tree.css('div[class*="product_list_filter_section"] li')
            
            for node in filter_items:
                cat_text = node.text(strip=True)
                if cat_text and len(cat_text) > 2:
                    # "(479)" jaise counts ko hatana
                    clean_text = cat_text.split('(')[0].strip().lower()
                    if clean_text and clean_text not in ["category", "categories"]:
                        categories_set.add(clean_text)
                        
        except Exception:
            pass # Ignore timeouts and move on

# ==========================================
# 🛑 PHASE 2: UNBXD API PRODUCT FETCHER
# ==========================================
async def fetch_products_from_api(session, category_name, all_products, unique_skus, semaphore):
    async with semaphore:
        page = 1
        rows = 100
        encoded_cat = urllib.parse.quote(category_name)
        current_time = int(time.time() * 1000)
        uid = f"uid-{current_time}-48347"
        
        items_found_in_this_cat = 0 # 🚀 Naya tracker
        
        while True:
            # 🚀 UPDATED API URL: Added 'variants=true' and 'pagetype=boolean' based on your payload
            api_url = f"https://search.unbxd.io/2f0815a68672fd25b4b7992b72302e5b/ss-unbxd-aapac-prod-sencogold56671721125516/search?q={encoded_cat}&rows={rows}&page={page}&uid={uid}&variants=true&pagetype=boolean&fields=title,sku,productUrl"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
                'Origin': 'https://sencogoldanddiamonds.com',
                'Referer': 'https://sencogoldanddiamonds.com/'
            }
            
            try:
                response = await session.get(api_url, headers=headers, impersonate="chrome120", timeout=20)
                
                # 🛑 DEBUGGER: Agar API gussa ho gayi toh error batayegi
                if response.status_code != 200:
                    # rprint(f"[red]⚠️ API Error {response.status_code} on category: {category_name}[/red]")
                    break
                    
                data = response.json()
                items = data.get('response', {}).get('products', [])
                
                if not items: 
                    break # Is page par aur items nahi hain
                    
                for item in items:
                    sku = item.get('sku')
                    if sku and sku not in unique_skus:
                        unique_skus.add(sku)
                        items_found_in_this_cat += 1
                        
                        title = item.get('title', '')
                        raw_url = item.get('productUrl', '')
                        full_url = raw_url if raw_url.startswith('http') else f"https://sencogoldanddiamonds.com/{raw_url.lstrip('/')}"
                        
                        all_products.append({
                            "Brand": "Senco",
                            "product_url": full_url,
                            "sku": sku,
                            "title": title,
                            "category": detect_category(title)
                        })
                
                page += 1
                await asyncio.sleep(0.5) # API ko block na hone dene ke liye slight delay
                
            except Exception as e:
                # rprint(f"[red]⚠️ Timeout/Error on {category_name}: {e}[/red]")
                break
                
        # 🟢 Agar is category se kuch naya mila toh console me print karo
        if items_found_in_this_cat > 0:
            rprint(f"[green] ↳ Extracted {items_found_in_this_cat} NEW items from '{category_name}'[/green]")
            
            # ==========================================
# 🚀 THE MASTER CONTROLLER
# ==========================================
async def main():
    rprint("\n[bold white on blue] ======================================== [/bold white on blue]")
    rprint("[bold white on blue]  🚀 SENCO 2-PHASE HYBRID SITEMAP SPIDER  [/bold white on blue]")
    rprint("[bold white on blue] ======================================== [/bold white on blue]\n")
    
    total_start_time = time.time()
    dynamic_categories = set()
    
    # -----------------------------------------------------
    # PHASE 1 EXECUTION
    # -----------------------------------------------------
    rprint("[bold yellow]🔄 PHASE 1: Harvesting Micro-Categories from URLs...[/bold yellow]")
    
    async with AsyncSession() as session:
        semaphore_p1 = asyncio.Semaphore(50) # 50 connections at a time
        
        with Progress(
            SpinnerColumn("dots", style="cyan"),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(complete_style="green", finished_style="green"),
            TaskProgressColumn(),
            TimeElapsedColumn()
        ) as progress:
            
            task1 = progress.add_task("[cyan]Scanning URLs...", total=len(RAW_SITEMAP_URLS))
            
            tasks = []
            for url in RAW_SITEMAP_URLS:
                task = asyncio.create_task(harvest_category_keywords(session, url, dynamic_categories, semaphore_p1))
                task.add_done_callback(lambda t: progress.update(task1, advance=1))
                tasks.append(task)
                
            await asyncio.gather(*tasks)
            
    categories_list = list(dynamic_categories)
    rprint(f"[bold green]✅ Phase 1 Complete! Found {len(categories_list)} unique categories to search.[/bold green]\n")

    # -----------------------------------------------------
    # PHASE 2 EXECUTION
    # -----------------------------------------------------
    rprint("[bold yellow]🔄 PHASE 2: Fetching All Products via Unbxd API...[/bold yellow]")
    
    all_final_products = []
    unique_skus = set()
    output_file = "senco_links_new.json"

    # Load existing data to avoid duplicates across multiple runs
    if os.path.exists(output_file):
        try:
            with open(output_file, "r", encoding="utf-8") as f:
                existing_data = json.load(f)
                all_final_products.extend(existing_data)
                for item in existing_data:
                    if item.get("sku"): unique_skus.add(item["sku"])
            rprint(f"[green]📂 Loaded {len(unique_skus)} existing SKUs from database.[/green]")
        except Exception: pass

    initial_count = len(unique_skus)

    async with AsyncSession() as session:
        semaphore_p2 = asyncio.Semaphore(20) # 20 parallel API calls (safe limit)
        
        with Progress(
            SpinnerColumn("bouncingBar", style="yellow"),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(complete_style="cyan", finished_style="green"),
            TaskProgressColumn(),
            TimeElapsedColumn()
        ) as progress:
            
            task2 = progress.add_task("[yellow]Querying API...", total=len(categories_list))
            
            tasks = []
            for cat in categories_list:
                task = asyncio.create_task(fetch_products_from_api(session, cat, all_final_products, unique_skus, semaphore_p2))
                task.add_done_callback(lambda t: progress.update(task2, advance=1))
                tasks.append(task)
                
            await asyncio.gather(*tasks)

    new_items = len(unique_skus) - initial_count
    total_time = round(time.time() - total_start_time, 2)

    # -----------------------------------------------------
    # SAVE & REPORT
    # -----------------------------------------------------
    if all_final_products:
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(all_final_products, f, indent=4)

    rprint("\n[bold green]" + "="*60 + "[/bold green]")
    rprint(f"[bold white on green] 🎉 FULL RUN COMPLETE! Saved {new_items} NEW items. [/bold white on green]")
    rprint(f"[bold cyan] 📦 Total Products in File: {len(all_final_products)} [/bold cyan]")
    rprint(f"[bold cyan] ⏱️ Total Time Taken: {total_time} seconds [/bold cyan]")
    rprint("[bold green]" + "="*60 + "[/bold green]\n")


if __name__ == "__main__":
    if os.name == 'nt':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())