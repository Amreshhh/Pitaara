# 🔄 Vercel Cron Job Setup Guide

## What Was Added

### 1. **New Cron Endpoint** (`api/main.py`)
- **Endpoint**: `GET /api/cron/update-rates`
- **Purpose**: Manually trigger the live rates cache update
- **Called by**: Vercel Cron automatically at scheduled time
- **Can also be**: Called manually for testing/on-demand updates

```bash
# Test manually:
curl https://your-backend.vercel.app/api/cron/update-rates
```

Response:
```json
{
  "status": "success",
  "message": "Cache updated successfully via Cron Job",
  "last_updated": "2026-05-09 12:00:00",
  "cache_status": "active",
  "rates_count": 4
}
```

---

### 2. **Cron Schedule Configuration** (`api/vercel.json`)
Added cron job schedule:

```json
"crons": [
  {
    "path": "/api/cron/update-rates",
    "schedule": "30 6 * * *"
  }
]
```

**Schedule Breakdown:**
- `30` = Minute (30)
- `6` = Hour (6 AM UTC)
- `*` = Every day of month
- `*` = Every month  
- `*` = Every day of week

---

## ⏰ Timezone Conversion: IST to UTC

| Time Zone | Time | Cron Expression |
|-----------|------|-----------------|
| **IST** (India) | 12:00 PM | - |
| **UTC** | 6:30 AM | `30 6 * * *` ✅ |

**Why?** IST = UTC + 5:30 hours
- 12:00 PM - 5:30 hours = 6:30 AM UTC

---

## 📅 How It Works

### **On Vercel (Production)**
1. Vercel Cron reads `api/vercel.json` `crons` array
2. Every day at **6:30 AM UTC** (= **12:00 PM IST**)
3. Automatically makes HTTP GET request to `/api/cron/update-rates`
4. Cache updates with latest live rates from all 4 brands
5. Frontend fetches fresh rates from `/api/live-rates`

### **On Local Machine (Development)**
1. APScheduler runs inside FastAPI lifespan
2. On server startup: Immediately fetch and cache rates
3. Every day at **12:00 PM** (server's local IST time): Auto-update cache
4. Can also manually call: `http://localhost:8000/api/cron/update-rates`

---

## 🧪 Testing the Cron Endpoint

### **Test 1: Verify Endpoint Works**
```bash
# From Vercel deployment URL
curl https://your-backend.vercel.app/api/cron/update-rates

# Or from local
curl http://localhost:8000/api/cron/update-rates
```

Expected Response:
```json
{
  "status": "success",
  "message": "Cache updated successfully via Cron Job",
  "last_updated": "2026-05-09 18:30:00",
  "cache_status": "active",
  "rates_count": 4
}
```

### **Test 2: Verify Live Rates Are Updated**
```bash
curl https://your-backend.vercel.app/api/live-rates
```

Check that `last_updated` timestamp is recent.

---

## 🐛 Troubleshooting

### **Cron Not Running on Vercel**
1. Check Vercel project settings → Cron Jobs
2. Verify endpoint `/api/cron/update-rates` returns 200 status
3. Check Vercel Function logs for errors
4. Ensure `api/vercel.json` has `crons` array (not root vercel.json)

### **Cache Not Updating**
1. Check if `fetch_and_cache_rates()` is working
2. Verify MongoDB connection (`MONGO_URI` env var set)
3. Check Vercel logs: `vercel logs api/main.py`
4. Try calling cron endpoint manually to see error

### **Wrong Timezone**
- If rates update at wrong time, check Vercel container timezone
- Current setup: `schedule: "30 6 * * *"` = 12:00 PM IST
- To change time: Update both `vercel.json` cron AND `cache_manager.py` scheduler

---

## 📝 Files Modified

| File | Change |
|------|--------|
| `api/main.py` | Added `/api/cron/update-rates` endpoint |
| `api/vercel.json` | Added `"crons"` array with daily schedule |
| `api/cache_manager.py` | Fixed scheduler time to 12:00 PM |

---

## ✅ Deployment Checklist

Before pushing to Vercel:

- [x] Verify `api/vercel.json` has `"crons"` array
- [x] Verify `/api/cron/update-rates` endpoint exists in `main.py`
- [x] Test endpoint locally: `curl http://localhost:8000/api/cron/update-rates`
- [x] Ensure `MONGO_URI` env var is set on Vercel
- [x] Push code to git
- [x] Vercel auto-deploys
- [ ] Wait 5 minutes, then test: `curl https://your-backend.vercel.app/api/cron/update-rates`
- [ ] Check `/api/live-rates` has fresh data

---

## 🚀 Next Steps

1. **Test locally first:**
   ```bash
   cd pythonscrapper
   uvicorn api.main:app --reload
   # In browser: http://localhost:8000/api/cron/update-rates
   ```

2. **Push to GitHub:**
   ```bash
   git add .
   git commit -m "Add: Vercel cron job for daily live rates update (12 PM IST)"
   git push origin master
   ```

3. **Verify on Vercel:**
   - Wait 2-3 minutes for build to complete
   - Check Vercel Deployments → Cron Jobs tab
   - Next scheduled run time should be visible
   - Manually test: `curl https://your-backend.vercel.app/api/cron/update-rates`

---

## 📞 Reference Docs

- Vercel Cron Docs: https://vercel.com/docs/cron-jobs
- Cron Expression Format: https://crontab.guru/
- APScheduler Docs: https://apscheduler.readthedocs.io/
