# AI-Powered Multimodal Construction Intelligence Platform

A full-stack, professional-grade construction intelligence web application for the Skillwallet capstone project.

**Frontend:** React.js + Vite + JavaScript (standard CSS, no Tailwind)  
**Backend:** Python 3.9+ + FastAPI + Uvicorn + Pydantic  
**AI:** Centralized Groq SDK integration (multimodal, JSON-contracted)  
**Database:** SQLite (SQLAlchemy) for project records, analysis history, reports  
**Image handling:** Multipart uploads, type/size validation, safe filenames

## Status

- **Frontend:** Fully implemented, production build verified (`npm run build` succeeds, 0 warnings, ~202 KB JS).
- **Backend:** Fully implemented and **verified at runtime**. FastAPI backend starts successfully on Python 3.14.10. All 11 API routes registered. Swagger UI at `/docs`.
- **Backend tests:** **22 passed, 0 failed** (pytest + FastAPI TestClient, run in demo mode).
- **Backend execution:** Verified working on Python 3.14.10 via the `py` launcher. The `python` command is not on PATH; use `py` instead (see Installation below).
- **Demo mode:** Enabled by default, returning clearly labelled deterministic schema-valid responses when no Groq credentials are configured.

## Table of Contents

1. [Architecture](#architecture)
2. [Folder Structure](#folder-structure)
3. [Features](#features)
4. [Environment Variables](#environment-variables)
5. [Installation](#installation)
6. [Running the Application](#running-the-application)
7. [API Endpoints](#api-endpoints)
8. [Example Requests](#example-requests)
9. [Testing](#testing)
10. [AI Configuration & Demo Mode](#ai-configuration--demo-mode)
11. [Known Limitations](#known-limitations)
12. [Deployment Considerations](#deployment-considerations)
13. [Security](#security)

## Architecture

The platform uses a clean separation of concerns:

- **React frontend (Vite)** — unified dashboard with hash-based routing, centralized API client (`src/api.js`), reusable components, dedicated page per feature, standard CSS styling.
- **FastAPI backend** — `app/main.py` wires CORS, startup DB init, and all routers under `/api`.
- **Centralized AI service** (`app/services/ai_service.py`) — all LLM interactions route through one shared service; feature modules never instantiate their own provider clients.
- **Feature services** — `safety_service.py`, `crack_service.py`, `planning_service.py`, `valuation_service.py`, `knowledge_service.py`, `daily_service.py`, `weather_service.py`.
- **Pydantic schemas** — explicit request/response contracts for every feature under `app/schemas/`.
- **CRUD + SQLAlchemy** — SQLite persistence for projects, analyses, reports under `app/crud/` and `app/database.py`.
- **File utils** — safe filename generation, upload type/size validation under `app/utils/file.py`.

### Data contract conventions

- Every success response: `{ success: true, data: {...}, meta: { feature, mode, model, request_id, timestamp } }`.
- Every error response: `{ success: false, error: <code>, message: <text>, details?: [...], meta: {...} }`.
- `mode` is one of `real_ai`, `demo`, `fallback` — always disclosed so the frontend never mistakes a simulated result for live analysis.
- Numerical outputs are returned as numbers, never formatted strings; units are documented in schemas.
- Image endpoints accept `multipart/form-data`; JSON endpoints accept `application/json`.

## Folder Structure

```
Construction-Intelligence/
├── README.md
├── .env.example                      # root placeholder (non-secret)
├── .gitignore
├── backend/
│   ├── .env.example                  # copy to .env, add real Groq key
│   ├── .gitignore
│   ├── requirements.txt              # pinned Python dependencies
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                   # FastAPI app, CORS, routers, startup
│   │   ├── config.py                 # all settings from env (python-dotenv)
│   │   ├── database.py               # SQLAlchemy SQLite engine, session, models
│   │   ├── api/
│   │   │   ├── deps.py
│   │   │   └── routers/
│   │   │       ├── health.py
│   │   │       ├── safety.py         # POST /safety/analyze (multipart)
│   │   │       ├── crack.py          # POST /crack/analyze (multipart)
│   │   │       ├── planning.py       # POST /planning/project
│   │   │       ├── valuation.py      # POST /valuation/property
│   │   │       ├── knowledge.py      # POST /knowledge/ask
│   │   │       ├── daily.py          # POST /daily-site/plan
│   │   │       └── weather.py        # POST /weather/advisory
│   │   ├── schemas/
│   │   │   ├── common.py             # APIResponse, ErrorResponse, HealthResponse, ResponseMeta
│   │   │   ├── safety.py
│   │   │   ├── crack.py
│   │   │   ├── planning.py
│   │   │   ├── valuation.py
│   │   │   ├── knowledge.py
│   │   │   ├── daily.py
│   │   │   └── weather.py
│   │   ├── services/
│   │   │   ├── ai_service.py         # centralized Groq client, JSON parsing, retries, demo/fallback
│   │   │   ├── safety_service.py
│   │   │   ├── crack_service.py
│   │   │   ├── planning_service.py   # backend-computed thumb-rule quantities/costs/schedule
│   │   │   ├── valuation_service.py  # backend-computed INR valuation, yield, ROI
│   │   │   ├── knowledge_service.py
│   │   │   ├── daily_service.py
│   │   │   └── weather_service.py    # GO/NO-GO/REVIEW with live/manual weather
│   │   ├── crud/
│   │   │   ├── project.py, analysis.py, report.py
│   │   ├── utils/
│   │   │   ├── file.py               # upload validation & safe storage
│   │   │   └── responses.py          # consistent success/error JSON helpers
│   │   ├── models/                   # (ORM models registered in database.py)
│   │   └── prompts/                  # feature prompts are inline in services
│   └── tests/
│       ├── conftest.py
│       ├── test_health.py
│       ├── test_schemas.py
│       ├── test_validation.py
│       └── test_demo_mode.py
└── frontend/
    ├── index.html
    ├── package.json
    ├── vite.config.js                # dev server on :5173, /api proxy to :8000
    ├── .gitignore
    └── src/
        ├── main.jsx
        ├── App.jsx                   # hash-router shell + Sidebar + Header
        ├── config.js                 # API base URL, timeout
        ├── api.js                    # centralized fetch client (JSON + FormData aware)
        ├── index.css                 # construction-inspired design system
        ├── components/
        │   ├── layout/Sidebar.jsx, Header.jsx
        │   ├── common/Button.jsx, Card.jsx, RiskBadge.jsx, LoadingSpinner.jsx, ErrorMessage.jsx
        │   └── upload/ImageUpload.jsx
        └── pages/
            ├── Dashboard.jsx
            ├── SafetyMonitor.jsx
            ├── CrackDetection.jsx
            ├── ProjectPlanner.jsx
            ├── RealEstateValuation.jsx
            ├── DailySiteAssistant.jsx
            ├── WeatherAdvisor.jsx
            └── KnowledgeAssistant.jsx
```

## Features

| # | Feature | Endpoint | Inputs | Output |
|---|---------|----------|--------|--------|
| 1 | Health check | `GET /api/health` | — | service status, Groq/vision/demo flags |
| 2.1 | Site Safety Monitoring | `POST /api/safety/analyze` | site photo (multipart) + optional observation log | risk level, hazards, PPE, corrective actions, disclaimer |
| 2.2 | Structural Crack Detection | `POST /api/crack/analyze` | crack photo + optional structural context | crack classification, severity, causes, risks, next steps |
| 3.1 | Project Planning | `POST /api/planning/project` | location, floors, area, type, use, quality | materials, INR cost estimate, schedule, milestones, layout |
| 3.2 | Indian Real Estate Valuation | `POST /api/valuation/property` | city, locality, type, area, unit, age, condition | INR value range, price/sqft, rental yield, ROI scenarios |
| 4.x | Centralized AI | internal (`app/services/ai_service.py`) | text or image+text | schema-validated JSON, demo/fallback labelling |
| 5.1 | Knowledge Base | Reference page (frontend) | search, category filter | materials, practices, terminology, safety reference |
| 5.2 | Construction Chatbot | `POST /api/knowledge/ask` | question + bounded history | concise answer + disclaimer |
| 5.3 | Daily Site Assistant | `POST /api/daily-site/plan`<br>`GET /api/daily-site/tasks`<br>`PATCH /api/daily-site/tasks/{task_id}/complete` | date, phase, activities, workforce, materials, equipment | prioritized tasks, safety checks, risks, follow-ups (task completion persisted in SQLite) |
| 5.4 | Weather Advisory | `POST /weather/advisory` | activity, location, time, optional manual conditions | GO / NO-GO / REVIEW REQUIRED + hazards + precautions |

### Dashboard
A landing page with summary cards and navigation to all eight feature modules: Site Safety Monitor, Crack Detection, Project Planner, Real Estate Valuation, Daily Site Assistant, Weather Advisor, Knowledge Base, and Construction Chatbot.

### Design
Dark left sidebar with orange (`#f97316`) construction accent, neutral backgrounds, accessible contrast, responsive cards, risk/decision badges, loading spinners, error alerts, empty states, and clear disclaimers on every AI result.

## Environment Variables

Create `backend/.env` from `backend/.env.example`. Never commit `.env`.

| Variable | Purpose | Example |
|---|---|---|
| `GROQ_API_KEY` | Groq API key (backend only) | `gsk_...` |
| `GROQ_MODEL_TEXT` | Text-only LLM model | `llama-3.1-8b-instant` |
| `GROQ_MODEL_VISION` | Vision-capable model for images | `llama-3.2-11b-vision-preview` |
| `VISION_ENABLED` | Enable vision model | `true`/`false` |
| `DEMO_MODE` | Deterministic demo responses when no credentials | `true` (default) |
| `LLM_REQUEST_TIMEOUT_SECONDS` | LLM call timeout | `60` |
| `LLM_MAX_RETRIES` | Bounded LLM retries | `2` |
| `MAX_UPLOAD_SIZE_MB` | Max image upload size | `10` |
| `ALLOWED_IMAGE_EXTENSIONS` | Allowed image extensions | `jpg,jpeg,png,webp` |
| `FRONTEND_ORIGIN` | CORS allowed origin | `http://localhost:5173` |
| `WEATHER_API_KEY` | Optional OpenWeatherMap key | `...` |
| `WEATHER_ENABLED` | Enable live weather | `true`/`false` |
| `DATABASE_URL` | SQLite DB path | `sqlite:///./construction_intelligence.db` |

## Installation

### Backend (Python 3.9+)

Python 3.14.10 is confirmed working. On this system, use the `py` launcher
(the `python` command is not on PATH).

Windows Command Prompt:
```
cd backend
py -m venv .venv
.venv\Scripts\activate
copy .env.example .env
py -m pip install -r requirements.txt
```

Windows PowerShell:
```
cd backend
py -m venv .venv
.\.venv\Scripts\Activate.ps1
Copy-Item .env.example .env
py -m pip install -r requirements.txt
```

Then edit `backend/.env` and set at least `GROQ_API_KEY` (or leave `DEMO_MODE=true` for demo mode).

**Dependency note:** The original pinned `pydantic==2.7.0` and `sqlalchemy==2.0.27` do not have Python 3.14 wheels and fail to build. `requirements.txt` now uses `pydantic>=2.10.0` and `sqlalchemy>=2.0.36`, which have pre-built cp314 wheels.


### Frontend (Node.js)

```
cd frontend
npm install
```

## Running the Application

### Backend
```
cd backend
# activate venv (see Installation above)
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```
Swagger UI: `http://127.0.0.1:8000/docs`

### Frontend
```
cd frontend
npm run dev          # http://localhost:5173
npm run build        # production build (verified clean)
npm run preview      # preview production build
```

The Vite dev server proxies `/api` to `http://localhost:8000`.

### Verified in this environment

- `py --version` → Python 3.14.10
- `py -m pip install -r requirements.txt` — succeeded (all packages installed, including pydantic 2.14.1 and sqlalchemy 2.1.6 with cp314 wheels).
- `py -m uvicorn app.main:app --reload` — backend starts successfully; `GET /api/health` returns `{"status":"ok",...}`.
- `py -m pytest tests/` — **22 passed, 0 failed**.
- `npm install` — succeeded (63 packages).
- `npm run build` — succeeded, 0 warnings, ~202 KB JS.
- All POST endpoints tested end-to-end via `Invoke-RestMethod` (planning, valuation, knowledge, daily, weather, safety/crack image validation).
- Daily task persistence verified (create → get → toggle complete → get again confirms state survives).


## API Endpoints

All under `/api`. Full interactive docs at `/docs` (Swagger UI) once the backend is running.

- `GET /health` — health check
- `POST /safety/analyze` — multipart: `site_photo`, `observation_log`, `safety_doc`
- `POST /crack/analyze` — multipart: `image`, `surface_type`, `element_type`, `age_years`, `noted_concerns`
- `POST /planning/project` — JSON (see `ProjectPlanningRequest`)
- `POST /valuation/property` — JSON (see `ValuationRequest`)
- `POST /knowledge/ask` — JSON: `{ message, history? }`
- `POST /daily-site/plan` — JSON (see `DailySiteRequest`); persists tasks to SQLite
- `GET /daily-site/tasks?plan_date=<date>` — retrieve persisted daily tasks
- `PATCH /daily-site/tasks/{task_id}/complete?plan_date=<date>` — toggle task completion (JSON: `{ task_id, completed }`)
- `POST /weather/advisory` — JSON (see `WeatherRequest`)

CORS is configured for `FRONTEND_ORIGIN` (default `http://localhost:5173`). Change `FRONTEND_ORIGIN` in `.env` for other origins.

## Example Requests

### Project planning (JSON)
```json
POST /api/planning/project
{
  "project_name": "Demo Villa",
  "location": "Mumbai",
  "construction_type": "residential",
  "intended_use": "house",
  "num_floors": 2,
  "plot_area": 300,
  "plot_area_unit": "sqm",
  "built_up_area": 200,
  "built_up_area_unit": "sqm",
  "quality_level": "medium"
}
```
Response includes `total_estimated_cost_inr`, `material_requirements`, `cost_categories`, `schedule_phases`, `milestones` — all numeric values (INR), never formatted strings.

### Property valuation (JSON)
```json
POST /api/valuation/property
{
  "city": "Pune",
  "locality": "Kothrud",
  "property_type": "residential",
  "area_value": 1000,
  "area_unit": "sqft",
  "condition": "good"
}
```
Response includes `indicative_value_min/max/mid_inr`, `estimated_price_per_sqft_inr`, `roi_scenarios`.

### Safety analysis (multipart)
```
POST /api/safety/analyze
form-data: site_photo=<image>, observation_log="Workers on scaffold without harness"
```

### Knowledge assistant (JSON)
```json
POST /api/knowledge/ask
{ "message": "What is the standard concrete mix ratio for M20?", "history": [] }
```

## Testing

Backend tests use pytest + FastAPI TestClient and run entirely in demo mode (no credentials needed):

```
cd backend
# activate venv (see Installation above)
py -m pytest -v
```

**22 tests pass, 0 failed.**

Test files:
- `test_health.py` — health check, root endpoint
- `test_schemas.py` — Pydantic request/response validation
- `test_validation.py` — invalid inputs (missing fields, negative area, empty message)
- `test_demo_mode.py` — demo responses conform to schemas, numeric fields are numbers
- `test_daily_tasks.py` — daily plan creation, task persistence, completion toggle, 404/400 handling
- `test_image_upload.py` — invalid file type rejection, valid image acceptance, valuation/planning validation

Frontend:
```
cd frontend
npm run build   # verified clean, 0 warnings
```


## AI Configuration & Demo Mode

- All AI credentials and model names are backend-only (env vars). Nothing is exposed to the frontend.
- `DEMO_MODE=true` (default) returns clearly labelled deterministic schema-valid responses; no Groq call is made.
- To use live AI: set `GROQ_API_KEY`, choose `GROQ_MODEL_TEXT`, and for image features set `GROQ_MODEL_VISION` to a Groq vision-capable model (e.g. `llama-3.2-11b-vision-preview`) and `VISION_ENABLED=true`, then `DEMO_MODE=false`.
- The centralized service validates every provider response against the feature Pydantic schema; invalid JSON or schema failures trigger controlled fallback, never malformed output to the UI.
- Demo/fallback results are visibly tagged with a `mode` badge ("DEMO", "FALLBACK", or "LIVE") and a `request_id`.

## Known Limitations

1. **`python` not on PATH** — Python 3.14.10 is installed but only reachable via the `py` launcher (`C:\Windows\py.exe`). Use `py -m venv`, `py -m pip`, `py -m uvicorn`, `py -m pytest` instead of `python`. See Installation above.
2. **Python 3.14 dependency compatibility** — `pydantic==2.7.0` and `sqlalchemy==2.0.27` lack Python 3.14 wheels and fail to build (require Rust/MSVC). `requirements.txt` now uses `pydantic>=2.10.0` and `sqlalchemy>=2.0.36` with pre-built cp314 wheels.
3. **Live AI (Groq)** not exercised — no `GROQ_API_KEY` provided; `DEMO_MODE=true` by default. All AI results are clearly labelled as demo. To use live AI: set `GROQ_API_KEY`, choose a `GROQ_MODEL_TEXT`, and for image features set `GROQ_MODEL_VISION` to a vision-capable model (e.g. `llama-3.2-11b-vision-preview`) with `VISION_ENABLED=true`, then `DEMO_MODE=false`.
4. **Live weather** requires `WEATHER_ENABLED=true` + `WEATHER_API_KEY` (OpenWeatherMap) plus network access. Otherwise the user supplies manual conditions, clearly labelled as "Manual input (user-provided)".
5. **Image analysis is AI-assisted and preliminary only** — not a certified safety inspection or structural diagnosis. No physical measurements (crack width/depth) are invented.
6. **Knowledge Base** is a static frontend reference (no document ingestion/retrieval implemented). The chatbot connects to the backend AI service but runs in demo mode without a Groq key.
7. **Conceptual visualization** in Project Planner is a locally rendered SVG block diagram, not an architectural drawing or AI-generated image.

## Deployment Considerations

- Set `ENVIRONMENT=production`, `DEBUG=false`, and a strong `SECRET_KEY`.
- Restrict `FRONTEND_ORIGIN` to your production frontend domain (do not leave `*` in production).
- Store `GROQ_API_KEY` and `WEATHER_API_KEY` in a secrets manager; never in source control.
- Serve `/uploads` and `/reports` behind authentication in production; the dev build stores them locally.
- Use a production WSGI/ASVI server (e.g. `uvicorn` with workers or behind nginx) rather than `--reload`.
- SQLite is the initial database; migrate to PostgreSQL if concurrent write load grows.

## Security

- Inputs validated on the backend (Pydantic + manual checks).
- Uploaded files restricted by type and size; stored with sanitized, unique filenames; never executed.
- Secrets kept on the backend only; `.env` and `.venv` gitignored.
- No stack traces exposed to users; consistent error envelopes.
- CORS deliberately configured via `FRONTEND_ORIGIN`.

## Commands to Start (summary)

Backend (after installing Python and activating venv):
```
cd backend
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Frontend:
```
cd frontend
npm run dev
```

Then open `http://localhost:5173`.
