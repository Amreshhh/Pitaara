# Pitaara - Real-Time Gold Calculator

Real-time gold price estimation across India's top jewellers with live rate scraping, instant calculations, and beautiful UI.

## 🎯 Features

- **Live Rate Scraping**: Auto-fetch gold rates from Tanishq, Malabar, Senco, Candere
- **Instant Calculation**: Price breakdowns with gold value, making charges, GST
- **Smart Caching**: Preserves rates on scraper failure; daily 12:00 PM updates
- **Dark/Light Theme**: Beautiful responsive UI with TailwindCSS
- **Coin Category**: Special handling for coin gold purchases
- **Range Search**: Flexible product search with elastic buffering

## 🚀 Quick Start (Local)

### Prerequisites
- Node.js 18+
- Python 3.9+
- MongoDB (Atlas or local)

### Setup

```bash
# 1. Clone and install dependencies
git clone https://github.com/YOUR_USERNAME/pythonscrapper.git
cd pythonscrapper

# 2. Backend setup
cd connection
cp .env.example .env
# Edit .env with MONGO_URI
pip install -r requirements.txt
uvicorn main:app --reload

# 3. Frontend setup (new terminal)
cd frontend
npm install
npm run dev

# 4. Visit http://localhost:3000
```

## 📁 Project Structure

See [STRUCTURE.md](STRUCTURE.md) for detailed folder organization.

```
pythonscrapper/
├── frontend/         # Next.js app (localhost:3000)
├── connection/       # FastAPI backend (localhost:8000)
├── .env             # Local secrets (GITIGNORED)
└── README.md        # This file
```

## 🌐 Deployment

### Frontend → Vercel

```bash
git push origin main
# Vercel auto-deploys from GitHub
```

### Backend → Railway.app

```bash
# 1. Railway.app account
# 2. Connect GitHub repo
# 3. Add MONGO_URI env var
# 4. Deploy
```

See [connection/README.md](connection/README.md) for detailed backend setup.

## 📝 Environment Setup

### .env (local only, not in git)
```
MONGO_URI=mongodb+srv://user:pass@cluster.mongodb.net/?retryWrites=true&w=majority
```

### .env.example (template, in git)
```
MONGO_URI=mongodb+srv://USERNAME:PASSWORD@cluster.mongodb.net/
ALLOWED_ORIGINS=http://localhost:3000,https://pythonscrapper.vercel.app
```

## 🔗 API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/categories` | GET | List jewellery categories |
| `/api/calculate-price` | POST | Calculate gold price |
| `/api/brand-summary` | POST | Brand analysis + scatter data |
| `/api/live-rates` | GET | Cached live gold rates |

## 🛠️ Key Technologies

| Layer | Stack |
|-------|-------|
| Frontend | Next.js, React 18, TailwindCSS, Recharts |
| Backend | FastAPI, Motor (async MongoDB), APScheduler |
| Scraping | curl_cffi (Chrome impersonation), BeautifulSoup, Selectolax |
| Deployment | Vercel (frontend), Railway (backend), MongoDB Atlas |

## 📊 Cache Architecture

```
Startup → Fetch all rates → GOLD_CACHE
                    ↓
           Daily 12:00 PM (APScheduler)
                    ↓
         Merge with prior cache (preserve failures)
                    ↓
        Frontend: /api/live-rates → localStorage
```

## 🐛 Troubleshooting

| Issue | Fix |
|-------|-----|
| MongoDB connection | Check `MONGO_URI` in `.env` |
| Rates showing stale data | Check APScheduler is running |
| CORS errors | Update `ALLOWED_ORIGINS` |

## 📄 License

MIT

---

**Status**: Production Ready  
**Last Updated**: May 7, 2026
```bash
python jewelry_scraper.py
```

## What it does

1. **Fetches HTML** asynchronously from 4 jewelry brand websites using `httpx`
2. **Analyzes content** using Google Gemini SDK with structured JSON output
3. **Validates data** using Pydantic models
4. **Stores in MongoDB** with upsert functionality

## Output Format

Data stored in MongoDB follows this structure:
```json
{
    "brand": "kalyan",
    "categories": {
        "Gold Rings": "₹300-500 per gram",
        "Gold Chains": "₹200-400 per gram",
        ...
    },
    "timestamp": "2024-02-10T12:00:00Z",
    "source_url": "https://..."
}
```

## Database

- **Database:** `jewelry_db`
- **Collection:** `making_charges`
- Updates existing records or inserts new ones based on brand name

## Features

✅ Async/await patterns for concurrent fetching  
✅ Structured output from Gemini API  
✅ Pydantic validation  
✅ MongoDB storage with upsert  
✅ Error handling for each step  
✅ Progress logging
