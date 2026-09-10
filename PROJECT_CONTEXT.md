# CareerLeap Business Model Dashboard — Project Context

## Overview

A full-stack web dashboard for modeling cohort economics at CareerLeap Academy. Users adjust business assumptions (participant fee, cohort size, career track, etc.) and instantly see revenue, costs, margins, pricing recommendations, sensitivity analysis, and annual projections.

## Architecture

- **Backend**: FastAPI (Python) — wraps the existing `cost_model.py` engine
- **Frontend**: React + Vite + Recharts — interactive dashboard with charts
- **Data**: JSON-driven career track and tool pricing configuration

## File Structure

```
clp_cost_model/
├── PROJECT_CONTEXT.md          # This file — project summary for AI assistance
├── README.md                   # Setup and run instructions
├── cost_model.py               # Original CLI engine (standalone, unchanged)
├── backend/
│   ├── __init__.py
│   ├── main.py                 # FastAPI routes: /api/calculate, /api/career-tracks
│   ├── models.py               # Pydantic request/response schemas
│   ├── career_tracks.py        # Loads career_tracks.json
│   ├── career_tracks.json      # Career track data: tools, prices, skills, sources
│   ├── requirements.txt        # fastapi, uvicorn, pydantic
│   └── .venv/                  # Python virtual environment
└── frontend/
    ├── package.json            # React, Vite, Recharts dependencies
    ├── vite.config.js          # Vite dev server with /api proxy to backend
    ├── index.html
    ├── README.md
    └── src/
        ├── main.jsx            # React entry point
        ├── App.jsx             # Main layout, state, API calls
        ├── api.js              # Fetch wrappers for backend endpoints
        ├── index.css           # Global styles
        └── components/
            ├── InputForm.jsx           # Assumptions form + career track dropdown
            ├── KPICards.jsx            # Top metrics: revenue, costs, margin, etc.
            ├── CareerTrackTools.jsx    # Selected track's tools, prices, sources
            ├── CostBreakdownChart.jsx  # Bar chart: revenue vs. costs
            ├── PricingTiersTable.jsx   # Recommended pricing tiers
            ├── AnnualProjection.jsx    # Annual summary cards
            └── SensitivityCharts.jsx   # Line charts for fee & cohort size sensitivity
```

## Backend API

### `GET /api/health`
Health check. Returns `{"status": "ok"}`.

### `GET /api/defaults`
Returns the default `CohortConfigInput` values.

### `GET /api/career-tracks`
Returns all career tracks with tools, prices, skills, and verification metadata.

### `POST /api/calculate`
Accepts a `CohortConfigInput` JSON body. Derives tool costs from the selected career track, runs the `CohortModel` engine, and returns:

- `config`: echo of input config
- `result`: revenue, costs, margins, break-even size, profit per participant
- `pricing_tiers`: recommended Budget / Standard / Premium / B2B pricing
- `sensitivity`: margin % curves for participant fee and cohort size
- `annual_projection`: annualized revenue, costs, margin for 4 cohorts/year
- `career_track`: full track details including tool breakdown

## Data Models

### `CohortConfigInput` (Pydantic)
- `participant_fee`: float, default 1200.0
- `cohort_size`: int, default 15
- `duration_months`: int, default 4
- `num_leads`: int, default 3
- `stipend_per_lead`: float, default 3000.0
- `overhead_per_participant`: float, default 150.0
- `tool_cost_per_user_per_month`: float, default 12.0 (overridden by career track)
- `fixed_tool_cost_per_month`: float, default 42.0
- `placement_bonus_per_lead`: float, default 0.0
- `no_show_rate`: float, default 0.05
- `refund_rate`: float, default 0.03
- `career_track`: str, default "it_infrastructure"

### `ToolBreakdownItem`
- `name`, `category`, `billing_model`
- `cost_per_user_per_month`, `cost_total_for_cohort`
- `free_tier_available`, `free_tier_limit`
- `why_chosen`
- `source_url`, `last_verified`

### `CareerTrackOutput`
- `key`, `label`, `short_name`
- `role_in_simulation`, `skills`
- `tools`: List[ToolBreakdownItem]
- `track_total_tool_cost`, `track_cost_per_participant`
- `total_tool_cost_per_user_per_month`

## Career Tracks Data

The system supports 3 career tracks defined in `backend/career_tracks.json`:

1. **IT Infrastructure & Support** (`it_infrastructure`)
   - Tools: Google Workspace, Google Admin Console, Jira, 1Password, Slack
   - Cost per user: €12.00/mo

2. **Data Analytics & Engineering** (`data_analytics`)
   - Tools: PostgreSQL, DuckDB, dbt Core, MotherDuck, Metabase, GitHub Actions, Railway/DigitalOcean
   - Cost per user: €1.00/mo

3. **Digital Marketing & Content** (`digital_marketing`)
   - Tools: Webflow, Ghost, Canva, Figma, Notion, Beehiiv, GA4, Google Search Console
   - Cost per user: €1.80/mo

Each tool includes `source_url` (official pricing page) and `last_verified` date for manual price verification.

## Core Engine Logic (`cost_model.py`)

### `CohortModel`
Calculates single-cohort economics:
- Revenue = participant_fee × cohort_size × (1 - no_show_rate - refund_rate)
- Tool costs = (tool_cost_per_user_per_month × cohort_size × duration_months) + (fixed_tool_cost_per_month × duration_months)
- Total costs = tool_costs + overhead + lead_costs + placement_bonuses
- Net margin = revenue - total_costs
- Margin % = net_margin / revenue × 100

### `AnnualProjection`
Multiplies single-cohort results by `cohorts_per_year` (default 4).

### `sensitivity(variable, range_pct)`
Runs what-if analysis by adjusting a variable by percentages and recalculating margin %.

## How to Run

### Backend
```bash
cd clp_cost_model
python3 -m venv backend/.venv
source backend/.venv/bin/activate
pip install -r backend/requirements.txt
uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

### Frontend
```bash
cd clp_cost_model/frontend
npm install
npm run dev
```

Open `http://localhost:5173`.

## Current Features

- Interactive form for all cohort assumptions
- Career track selector with per-track tool breakdown
- KPI cards: revenue, total costs, net margin, margin %, break-even size, profit per participant
- Revenue & cost breakdown bar chart
- Recommended pricing tiers table
- Annual projection cards
- Sensitivity analysis charts (participant fee, cohort size)
- Tool pricing source links and verification dates

## Potential Extensions / Areas for Help

- Add user authentication and saved scenarios
- Persist configurations to a database (SQLite/PostgreSQL)
- Add CSV/PDF export of dashboard results
- Add more career tracks or make tracks user-editable via UI
- Add historical trend tracking across multiple cohorts
- Add currency conversion (EUR/USD)
- Add tax/VAT modeling
- Add team lead cost breakdown by role
- Add scenario comparison (side-by-side what-if analysis)
- Add alerts when margin falls below thresholds
- Dockerize for easier deployment
- Add unit and integration tests

## Notes for AI Assistance

When asking for help:
- Mention the file paths above so the AI knows the project layout
- The backend uses Python 3.9, so avoid `X | Y` type syntax — use `Optional[X]` instead
- The frontend uses React 18 + Vite 5 + Recharts 2.x
- Career track data lives in `backend/career_tracks.json` — edit there to change tools/prices
- The original `cost_model.py` at the project root is standalone and should not be modified
