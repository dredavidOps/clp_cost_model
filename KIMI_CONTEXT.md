# CareerLeap Dashboard — Context for Kimi Online

## What this is

A full-stack FastAPI + React business-model dashboard for CareerLeap Academy. It wraps a standalone `cost_model.py` engine and adds a career-track selector that loads per-track tools and prices from `backend/career_tracks.json`.

This is the **simpler, earlier build** (PROJECT_CONTEXT.md version), not the v5 Excel-replica expansion. The v5 files are archived in `v5_backup/` if you ever want to switch back.

## How to run locally

```bash
# Backend
source backend/.venv/bin/activate
pip install -r backend/requirements.txt
uvicorn backend.main:app --host 127.0.0.1 --port 8000

# Frontend (new terminal)
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`. Vite proxies `/api` to the FastAPI backend.

## File tree

```
clp_cost_model/
├── backend/
│   ├── main.py              # FastAPI routes
│   ├── models.py            # Pydantic request/response schemas
│   ├── career_tracks.py     # Loads career_tracks.json
│   ├── career_tracks.json   # 3 tracks + tools/prices/sources
│   └── requirements.txt
├── frontend/src/
│   ├── App.jsx              # State + layout
│   ├── api.js               # Fetch wrappers
│   ├── index.css            # Styles
│   └── components/
│       ├── InputForm.jsx
│       ├── KPICards.jsx
│       ├── CareerTrackTools.jsx
│       ├── CostBreakdownChart.jsx
│       ├── PricingTiersTable.jsx
│       ├── AnnualProjection.jsx
│       └── SensitivityCharts.jsx
├── cost_model.py            # Standalone cohort economics engine (do not modify)
├── README.md
├── PROJECT_CONTEXT.md
└── v5_backup/               # Archived v5 expansion files
```

## Backend API

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Health check |
| GET | `/api/defaults` | Default cohort assumptions |
| GET | `/api/career-tracks` | All tracks with tools, skills, prices, source URLs |
| POST | `/api/calculate` | Run model and return dashboard payload |

### POST `/api/calculate` body example

```json
{
  "participant_fee": 1200,
  "cohort_size": 15,
  "duration_months": 4,
  "num_leads": 3,
  "stipend_per_lead": 3000,
  "overhead_per_participant": 150,
  "tool_cost_per_user_per_month": 12,
  "fixed_tool_cost_per_month": 42,
  "placement_bonus_per_lead": 0,
  "no_show_rate": 0.05,
  "refund_rate": 0.03,
  "career_track": "it_infrastructure"
}
```

### Response shape

```json
{
  "config": { ... },
  "result": {
    "revenue", "tool_costs", "overhead", "lead_costs",
    "total_costs", "net_margin", "margin_pct", ...
  },
  "pricing_tiers": [...],
  "sensitivity": { "participant_fee": [...], "cohort_size": [...] },
  "annual_projection": { ... },
  "career_track": { "key", "label", "skills", "tools", ... },
  "tool_breakdown": [...]
}
```

## Core calculation (from `cost_model.py`)

```python
effective_participants = cohort_size * (1 - no_show_rate - refund_rate)
revenue = participant_fee * effective_participants

tool_costs = (
    tool_cost_per_user_per_month * cohort_size * duration_months
    + fixed_tool_cost_per_month * duration_months
)
overhead = overhead_per_participant * cohort_size
lead_costs = stipend_per_lead * num_leads
placement_bonuses = placement_bonus_per_lead * num_leads
total_costs = tool_costs + overhead + lead_costs + placement_bonuses

net_margin = revenue - total_costs
margin_pct = net_margin / revenue * 100
break_even_size = total_costs / participant_fee
```

## Career tracks and tool costs

| Track | Monthly cost / user | Total cohort tool cost |
|-------|---------------------|------------------------|
| IT Infrastructure & Support | €12.00 | €720.00 |
| Data Analytics & Engineering | €1.00 | €60.00 |
| Digital Marketing & Content | €1.80 | €108.00 |

Each tool in `career_tracks.json` contains `source_url` and `last_verified`. To verify current prices, open the `source_url` and update `last_verified`.

## Frontend state flow

1. `App.jsx` mounts and fetches `/api/defaults` + `/api/career-tracks`.
2. It immediately posts the defaults to `/api/calculate`.
3. The user changes an input (including the career-track dropdown) and clicks **Update Dashboard**.
4. `App.jsx` re-posts to `/api/calculate` and re-renders all panels.

## Things you can ask Kimi to do with this project

- "Add a CSV/PDF export button to the dashboard."
- "Add a second chart that shows cost breakdown by category."
- "Persist saved scenarios to localStorage or a database."
- "Add user authentication and per-user saved cohorts."
- "Dockerize the whole stack."
- "Switch back to the v5 expansion by restoring files from `v5_backup/`."

## Important constraints

- React 18, Vite 5, Recharts 2.x, FastAPI 0.111, Pydantic 2.7, Python 3.9.
- Do **not** modify `cost_model.py` at the project root.
- Keep tool price source URLs up to date in `backend/career_tracks.json`.

## Current status

- Backend starts cleanly at `http://127.0.0.1:8000`.
- Frontend starts cleanly at `http://localhost:5173`.
- Dashboard renders with the default cohort (15 participants, €1,200 fee, IT track).
- Switching career tracks updates the tool list and per-user tool cost.
