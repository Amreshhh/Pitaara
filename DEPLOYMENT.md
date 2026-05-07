# Deployment Checklist & Guide

Prepare Pitaara for production deployment to Vercel (frontend) + Railway (backend).

## Pre-Deployment Checklist

### 1. Code Cleanup ✓
- [x] Remove old `backend/` folder (archived in `.archive/`)
- [x] Clean `connection/` to only essential files
- [x] Organize folder structure per STRUCTURE.md

### 2. Dependencies ✓
- [x] `connection/requirements.txt` - cleaned & minimal
- [x] `frontend/package.json` - dependencies frozen
- [x] No duplicate/unused packages

### 3. Environment & Secrets ✓
- [x] `.env` created (GITIGNORED) with real values
- [x] `.env.example` created with placeholders
- [x] All secrets removed from code
- [x] `.gitignore` updated with all cache/build folders

### 4. Git & Repo ✓
- [ ] `git init` (if not done)
- [ ] `git add .`
- [ ] `git commit -m "Initial: Clean organization for deployment"`
- [ ] Create GitHub repo
- [ ] `git remote add origin https://github.com/YOUR_USERNAME/pythonscrapper.git`
- [ ] `git push -u origin main`

### 5. Configuration Files ✓
- [x] `connection/.env.example` - updated
- [x] `.env.example` - created
- [x] `connection/vercel.json` - exists (for serverless)
- [x] `next.config.mjs` - configured

---

## Deployment Steps

### Step 1: Push to GitHub

```bash
cd c:\Users\Asus\Downloads\pythonscrapper
git add .
git commit -m "chore: organize folder structure for deployment"
git push -u origin main
```

### Step 2: Deploy Frontend to Vercel

1. **Go to [vercel.com](https://vercel.com)**
2. **Sign in with GitHub**
3. **"Import Project"**
4. **Select pythonscrapper repo**
5. **Configure:**
   - Framework: Next.js
   - Root Directory: `frontend/`
   - Environment Variables:
     ```
     NEXT_PUBLIC_API_URL=https://your-railway-backend-url
     ```
6. **Deploy** → Wait 2-3 min → Get URL like `https://pythonscrapper.vercel.app`

### Step 3: Deploy Backend to Railway.app

1. **Go to [railway.app](https://railway.app)**
2. **Login with GitHub**
3. **"New Project"**
4. **"Deploy from GitHub repo"**
5. **Select pythonscrapper**
6. **Configure:**
   - Build: `pip install -r connection/requirements.txt`
   - Start: `cd connection && uvicorn main:app --host 0.0.0.0 --port $PORT`
   - Environment Variables:
     ```
     MONGO_URI=<your_mongodb_atlas_uri>
     PORT=8000
     ```
7. **Deploy** → Get backend URL like `https://pythonscrapper-api.railway.app`

### Step 4: Update Frontend API URL

1. **In Vercel project settings:**
   - Environment Variables → Edit `NEXT_PUBLIC_API_URL`
   - Paste your Railway backend URL
   - **Trigger Redeploy**

2. **Verify in code** (check these files use env var):
   - [frontend/hooks/useLiveRates.js](../frontend/hooks/useLiveRates.js)
   - [frontend/hooks/useGoldCalculator.js](../frontend/hooks/useGoldCalculator.js)
   - [frontend/components/BrandModal.jsx](../frontend/components/BrandModal.jsx)

---

## Post-Deployment Verification

### Test Frontend
```bash
# Open in browser
https://pythonscrapper.vercel.app

# Should show:
- Live cache indicator (✅ Live Cache)
- Categories dropdown populated
- Can select weight & purity
- FIND button works
```

### Test Backend
```bash
# Check endpoints
curl https://your-railway-api-url/api/categories
curl https://your-railway-api-url/api/live-rates

# Should return JSON with no errors
```

### Test Integration
1. Open frontend at https://pythonscrapper.vercel.app
2. Select category → weight → click FIND
3. Verify brand cards load with prices
4. Click on brand → modal should load scatter data
5. Check network tab (DevTools) → requests to `/api/` should use Railway URL

---

## Troubleshooting

### CORS Error
**Problem:** Frontend requests fail with CORS error
**Fix:** Update `ALLOWED_ORIGINS` in Railway backend env vars

### Rates showing stale data
**Problem:** Live rates not updating
**Fix:** Check APScheduler is running in Railway logs

### MongoDB connection failed
**Problem:** Backend can't connect to MongoDB Atlas
**Fix:** 
1. Verify `MONGO_URI` in Railway env vars
2. Check MongoDB Atlas IP whitelist includes Railway's IP (or set to 0.0.0.0)

### Vercel build failing
**Problem:** Frontend deployment stuck
**Fix:**
1. Check logs in Vercel dashboard
2. Ensure `frontend/` root directory is set in Vercel project settings
3. Verify `next.config.mjs` is valid

---

## Rollback Plan

If deployment fails:

```bash
# Revert to last working commit
git log --oneline
git reset --hard <last_working_commit>
git push -f origin main

# Re-trigger deployment in Vercel/Railway
```

---

## Next Steps After Deployment

1. **Add custom domain** (optional)
2. **Enable Vercel Analytics**
3. **Setup uptime monitoring** (Uptime Robot)
4. **Create CI/CD pipeline** (GitHub Actions)
5. **Add production logging** (Sentry)

---

**Status**: Ready for Deployment  
**Estimated Time**: 30 minutes  
**Last Updated**: May 7, 2026
