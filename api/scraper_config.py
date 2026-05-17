"""
Scraper configuration - Removed all hardcoded and JSON fallback logic
since they don't work on Vercel serverless environment.

Architecture: MongoDB → Live Scrape → Error
No fallback rates. Errors handled at API level only.
"""
