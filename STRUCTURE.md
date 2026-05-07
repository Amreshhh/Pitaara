# Project Structure Guide

## Overview
Pitaara: Real-time gold price calculator across India's top jewellers.

```
pythonscrapper/
├── frontend/                    # Next.js React app (frontend)
│   ├── app/
│   ├── components/
│   ├── hooks/
│   ├── lib/
│   ├── public/
│   ├── package.json
│   └── next.config.mjs
│
├── connection/                  # FastAPI backend (core)
│   ├── main.py                 # FastAPI endpoints
│   ├── live_rates.py           # Web scraper (rates)
│   ├── cache_manager.py        # Cache + scheduler
│   ├── scraper_config.py       # Fallback rates
│   ├── requirements.txt        # Dependencies
│   ├── .env.example            # Environment template
│   ├── vercel.json            # Deployment config
│   └── README.md              # Setup instructions
│
├── .env                         # Local secrets (GITIGNORED)
├── .gitignore                  # Git exclusions
├── README.md                   # Root documentation
└── utils.py                    # Shared utilities
```

## Folders to Archive/Remove

Move to `.archive/` if needed for reference:
- `backend/` - Old scraper code (fetch_prod_*)
- **NOT IN GIT**: `.venv/`, `__pycache__/`, `.next/`

## Essential Files for Deployment

### Frontend
- `frontend/package.json`
- `frontend/next.config.mjs`
- All code in `app/`, `components/`, `hooks/`, `lib/`

### Backend
- `connection/main.py`
- `connection/live_rates.py`
- `connection/cache_manager.py`
- `connection/scraper_config.py`
- `connection/requirements.txt`
- `connection/.env.example`

### Root
- `.gitignore`
- `.env` (local only, NOT pushed)
- `README.md`

## Not in GIT (See .gitignore)

```
.env                    # Secrets
.venv/                  # Virtual env
__pycache__/            # Python cache
node_modules/           # Node packages
.next/                  # Next.js build
.vercel/                # Vercel cache
```

## Deployment Checklist

- [ ] All `.env` vars in `.env.example`
- [ ] No secrets in code
- [ ] `requirements.txt` clean and minimal
- [ ] `.gitignore` excludes all cache/venv/secrets
- [ ] `frontend/` builds without errors
- [ ] `backend/` runs locally: `uvicorn connection.main:app`

---

Last Updated: May 7, 2026
