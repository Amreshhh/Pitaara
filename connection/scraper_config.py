# Scraper Configuration and Fallback Rates
# Use these values when live scraping fails for a particular brand.

SCRAPER_FALLBACK_RATES = {
    "Tanishq": {
        "24K": 15200,
        "22K": 13900,
        "18K": 11400,
        "14K": 8900,
    },
    "Malabar": {
        "24K": 15100,
        "22K": 13800,
        "18K": 11300,
        "14K": 8800,
    },
    "Senco": {
        "24K": 15300,
        "22K": 14000,
        "18K": 11500,
        "14K": 8950,
    },
    "Candere": {
        "24K": 15200,
        "22K": 13900,
        "18K": 11400,
        "14K": 8900,
    },
}

# Fallback rates for specific purity levels when partial scraping fails
# Tanishq Fallback: 22K rate when DOM fails
TANISHQ_22K_FALLBACK = 13900  # Used in fetch_tanishq if DOM parsing fails

# Candere Fallback: 24K rate when DOM fails
CANDERE_24K_FALLBACK = 15200  # Used in fetch_candere if DOM parsing fails
