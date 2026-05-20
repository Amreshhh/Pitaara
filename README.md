# Pitaara — Gold Rates Scraper & Calculator

This repository contains the backend scrapers and a Next.js frontend used to aggregate live gold rates from multiple jewellers and provide instant price calculations.

Key components:
- `api/` — FastAPI backend providing live-rates, brand summaries and webhook endpoints.
- `backend/` — historical scraping helpers and ad-hoc scripts used for data processing.
- `frontend/` — Next.js (app directory) UI and client logic.

This README focuses on getting the project running locally and explains where to find key code and docs.

## Quick Start (Local)

### Prerequisites
- Node.js 18+
- Python 3.9+
- MongoDB (Atlas or local)

### Run the backend (development)

```bash
# from repository root
python -m pip install -r api/requirements.txt
# start FastAPI app
uvicorn api.main:app --reload --port 8000
```

The backend exposes endpoints under `http://localhost:8000/api/...`.

### Run the frontend (development)

```bash
cd frontend
npm install
npm run dev
```

Frontend will be available at `http://localhost:3000` by default.

## Environment variables
Create an `.env` file (or set env vars in your run environment). Common variables used by this project:

- `MONGO_URI` — MongoDB connection string
- `BACKEND_API_URL` — Public URL of backend (used by frontend and callbacks)
- `GITHUB_TOKEN` — Optional: used to dispatch GitHub Actions for isolated scrapes
- `GITHUB_REPOSITORY` — Optional: owner/repo used when dispatching workflows
- `TANISHQ_CALLBACK_SECRET` — Optional secret for authenticated callbacks
- `ENABLE_GITHUB_TANISHQ_DISPATCH` — `true`/`false` to allow workflow dispatching

Only set tokens/secrets for CI or production; never commit them to the repo.

## Key Code Locations

- Backend API: [api/main.py](api/main.py) — main FastAPI routes and live-rates logic
- Tanishq fetcher: [api/tanishq_fetcher.py](api/tanishq_fetcher.py)
- GH Actions worker: [.github/workflows/tanishq-live-rates.yaml](.github/workflows/tanishq-live-rates.yaml) and [api/github_actions_tanishq.py](api/github_actions_tanishq.py)
- Frontend hook: `frontend/hooks/useLiveRates.js` — SWR-like stale-while-revalidate logic
- Brand UI: `frontend/components/BrandModal.jsx` — includes performance scatter chart

## How live rates flow works (short)

- The backend keeps a single canonical document in MongoDB (`Cron_live_rates`, `_id: "latest"`).
- Scheduled jobs or external triggers refresh brand rates and merge them into the cached doc while preserving failed brand entries.
- Tanishq scraping is executed in an isolated workflow (GitHub Actions) and posts results back to a callback endpoint; this protects the backend from site blocking and long-running browser tasks.
- The frontend requests `/api/live-rates` and displays cached values immediately while triggering background refreshes when data is stale.

## Docs and housekeeping

This repository previously contained multiple standalone Markdown docs. Most documentation is now consolidated into in-code README snippets and the `docs/` folder when needed. If you are looking for architecture diagrams or the live-rates flow, see `api/README.md` or open the `docs/` folder if present.

## Deployment

- Frontend: deploy `frontend/` to Vercel or any static/SSR host that supports Next.js.
- Backend: deploy `api/` to Railway, Render, or any container host. Ensure `MONGO_URI` and callback secrets are set in your deployment.
- Optional: create a GitHub Actions workflow for scheduled dispatch or use your host's scheduler to call the backend cron endpoints.

## Troubleshooting

- If rates appear stale: check the backend logs and ensure `APScheduler` or your cron runner is executing the refresh job.
- If GitHub workflow dispatches fail: confirm `GITHUB_TOKEN` and `GITHUB_REPOSITORY` are present and the configured workflow `ref` matches your branch (commonly `master` or `main`).

## Contributing

Open an issue or submit a pull request. Please keep secrets out of commits and include reproducible steps for scraping-related fixes.

---
**Last Updated**: May 20, 2026

