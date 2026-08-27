# Coinsy Finance - Deployment & Infrastructure Guide

This guide details step-by-step instructions for containerizing and deploying Coinsy Finance to production platforms (Railway, Render, Vercel, Netlify) with managed PostgreSQL, secrets management, CORS security, and background scheduler monitoring.

---

## Technical Stack Architecture

- **Backend**: Containerized FastAPI application running via Docker on Railway or Render.
- **Database**: Managed PostgreSQL instance (Railway Postgres or Render PostgreSQL).
- **Frontend**: Production React Vite Single Page Application (SPA) deployed on Vercel or Netlify.
- **Scheduler**: Asynchronous background thread scheduler running inside the FastAPI lifespan process.

---

## 1. Backend Deployment (Railway or Render)

### Option A: Deploying on Railway (Recommended)

1. **Provision Database**:
   - In Railway dashboard, click **New Project** -> **Provision PostgreSQL**.
   - Copy the generated `DATABASE_URL` string.

2. **Deploy Backend Container**:
   - Click **Add Service** -> **GitHub Repo** -> select `Coinsy-Finance`.
   - Set Root Directory to `/backend`. Railway will automatically detect [`Dockerfile`](file:///Users/karunya/Coinsy%20Finance/backend/Dockerfile).
   - In **Variables** tab, set:
     - `DATABASE_URL`: `${{ Postgres.DATABASE_URL }}` (or connected PostgreSQL string)
     - `SECRET_KEY`: `your-secure-random-jwt-secret`
     - `ANTHROPIC_API_KEY`: `sk-ant-api03-xxxx`
     - `ALLOWED_ORIGINS`: `https://coinsy-finance.vercel.app,https://coinsy-finance.netlify.app`
     - `PORT`: `8000`

3. **Expose Public URL**:
   - In service Settings -> **Networking**, click **Generate Domain** (e.g. `https://coinsy-backend.up.railway.app`).

---

### Option B: Deploying on Render

1. **Deploy using Infrastructure Blueprint**:
   - In Render dashboard, click **New** -> **Blueprint**.
   - Point to `backend/render.yaml`. Render will automatically provision both the Managed PostgreSQL database and the Docker Web Service.

2. **Configure Environment Secrets**:
   - In Render Dashboard -> Web Service -> **Environment**, fill in `ANTHROPIC_API_KEY` and update `ALLOWED_ORIGINS`.

---

## 2. Frontend Deployment (Vercel or Netlify)

### Option A: Deploying on Vercel (Recommended)

1. **Create New Project**:
   - In Vercel dashboard, click **Add New** -> **Project** -> Import `Coinsy-Finance`.
   - Set **Root Directory** to `frontend`.
   - Framework Preset: **Vite**.
   - Build Command: `npm run build`, Output Directory: `dist`.

2. **Set Environment Variable**:
   - Under **Environment Variables**, add:
     - `VITE_API_URL`: `https://your-backend.up.railway.app/api/v1` (or your deployed backend URL).

3. **Deploy**:
   - Click **Deploy**. Vercel will build the SPA bundle and apply routing rules from [`vercel.json`](file:///Users/karunya/Coinsy%20Finance/frontend/vercel.json).

---

### Option B: Deploying on Netlify

1. **Connect Repository**:
   - In Netlify dashboard, click **Add new site** -> **Import from existing project**.
   - Base directory: `frontend`, Build command: `npm run build`, Publish directory: `frontend/dist`.
   - Netlify automatically detects routing configuration from [`netlify.toml`](file:///Users/karunya/Coinsy%20Finance/frontend/netlify.toml).

2. **Set Build Environment**:
   - Add `VITE_API_URL` pointing to your deployed FastAPI backend.

---

## 3. Uptime Monitoring & Scheduled Jobs Verification

- **Health Check Endpoint**:
  Access `GET https://your-backend.up.railway.app/api/v1/health` in browser or uptime monitoring service (e.g., UptimeRobot).
  Expected response:
  ```json
  {
    "status": "ok",
    "database": "healthy",
    "scheduler_running": true,
    "allowed_origins": ["https://coinsy-finance.vercel.app"]
  }
  ```

- **Scheduler Verification**:
  The background scheduler initializes inside FastAPI lifespan hooks (`app/main.py`), ensuring spend predictions and daily tips pre-compute continuously in production off the main HTTP thread.

---

## 4. Production Smoke Test Checklist

Perform the following verification steps on the live frontend URL:

1. **User Signup & Auth**:
   - Register a new account at `/signup`.
   - Confirm JWT token persistence and automatic redirect to `/dashboard`.
2. **First-Import Consent & Statement Upload**:
   - Navigate to `/import`.
   - Confirm the First-Import Privacy Consent modal renders.
   - Upload a CSV or PDF statement and verify transactions are auto-categorized with account numbers redacted.
3. **Dashboard & Visualizations**:
   - Confirm Category Donut Chart, Comparison Bar Chart, and Trend Line Chart render.
   - Toggle Weekly / Monthly / Yearly views.
4. **Budget Goal Setup & Threshold Alert**:
   - Navigate to `/budgets`.
   - Set a monthly cap for a category and verify the progress bar and alert badge (`80% NEAR LIMIT` or `100% OVER BUDGET`).
5. **Coinsy Mascot Companion Interaction**:
   - Click floating Coinsy mascot at bottom-right.
   - Verify 6 mood states, cursor eye tracking, and companion chat responses via "Ask Coinsy".
