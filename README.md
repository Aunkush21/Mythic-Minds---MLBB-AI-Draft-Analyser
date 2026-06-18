# MythicMinds — MLBB AI Draft Intelligence

AI-powered draft intelligence, hero recommendations, and build optimization for **Mobile Legends: Bang Bang**.

**Live app:** https://mythicmind.vercel.app
**API:** https://mythicminds-api.onrender.com

> Unofficial fan project — not affiliated with or endorsed by Moonton. All Mobile Legends: Bang Bang assets, trademarks, and content belong to Moonton.

---

## Features

- **Draft Room** — live draft simulation with win-probability prediction as picks/bans come in
- **Hero Recommendation** — suggests the next pick based on the current draft state, synergy, and counters
- **Hero Compendium** — browsable hero database with stats, counters, synergies, and a similarity engine ("heroes like this one")
- **Build Explorer** — recommended item/emblem/battle-spell builds per hero, role-aware and explainable
- **Meta Dashboard** — patch-aware win/pick/ban rate trends
- **Yss the mascot** — a reactive companion that responds to draft events, with a tap-to-ask FAQ chat
- Light/dark theme, fully responsive layout

## Tech stack

| Layer | Stack |
|---|---|
| Frontend | React 19, TypeScript, Vite, Tailwind CSS, Zustand, React Query, React Router, Framer Motion |
| Backend | FastAPI, SQLAlchemy 2.0 (async), Pydantic v2, Uvicorn |
| ML | XGBoost win predictor, hero similarity matrix, rule-based build recommendation engine, SHAP-based explainability |
| Database | PostgreSQL |
| Hosting | Vercel (frontend) · Render (backend) · Neon (Postgres) |

## Architecture

```
frontend/   React SPA — calls the backend over /api/v1
backend/    FastAPI app — serves REST endpoints, owns the DB connection,
            imports ml/ in-process (loads the trained model + lookup
            tables once at startup, not per request)
ml/         Feature engineering, model training, recommendation/
            build-recommendation engines, trained model artifacts
database/   schema.sql + migrations + seed scripts (PostgreSQL)
```

The backend isn't a thin wrapper around a separate ML microservice — `ml/` is imported directly into the FastAPI process (see `backend/app/services/ml_bridge.py`), so there's a single deployable backend service.

## API endpoints

All prefixed with `/api/v1`:

- `GET /heroes`, `GET /heroes/{id}`, `GET /heroes/{id}/similar`
- `GET /items`, `GET /counters`, `GET /emblems`, `GET /battle-spells`, `GET /patches`, `GET /patches/current`
- `POST /win-probability` — win prediction for a given draft state
- `POST /hero-pick` — recommended next pick
- `POST /build` — recommended item/emblem/spell build for a hero
- `POST /admin/refresh-ml-data` — reload ML caches without a redeploy

Health check: `GET /health`.

## Running locally

**Prerequisites:** Node 20+, Python 3.11+, a PostgreSQL database.

### 1. Database

```bash
psql <your-database-url> -f database/schema.sql
psql <your-database-url> -f database/migrations/001_add_patch_history.sql
psql <your-database-url> -f database/migrations/002_dedupe_hero_builds.sql
psql <your-database-url> -f database/migrations/003_fix_boots_movement_speed.sql

cd database
DATABASE_URL=<your-database-url> python seed_all.py
```

### 2. Backend

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env   # fill in DATABASE_URL, CORS_ORIGINS
python -m uvicorn app.main:app --reload --port 8000
```

### 3. Frontend

```bash
cd frontend
npm install
cp .env.example .env   # VITE_API_BASE_URL=/api/v1 for local dev (uses the Vite proxy)
npm run dev
```

Frontend runs at `http://localhost:5173` and proxies `/api` to the backend at `http://127.0.0.1:8000` in dev.

## Deployment notes

- **Database (Neon):** free serverless Postgres, scales to zero, auto-wakes on the next query.
- **Backend (Render free tier):** spins down after ~15 minutes of inactivity; first request after idle can take 30–50s while it cold-starts and re-warms the ML caches (model + lookup tables loaded once at startup).
- **Frontend (Vercel):** `VITE_API_BASE_URL` is baked in at build time, so it must point at the live backend URL before deploying, not after.
