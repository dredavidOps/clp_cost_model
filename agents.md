# CareerLeap Pricing Dashboard — Agent Guide

## 1. Project overview

This is the **CareerLeap Pricing Dashboard**, a full-stack web application that replicates the economics of the `CareerLeap_Pricing_Broad.xlsx` workbook as an interactive model. Users edit assumptions about cohort size, per-workstream tooling, mentor hours, internal-team stipends, operational costs, other costs, and seat pricing; the dashboard recalculates revenue, costs, margins, break-even prices, cash-flow timing, and launch readiness in real time.

**Important reality check:** The running code in `backend/` and `frontend/src/` implements the **v5 Excel-replica pricing model** described in `CareerLeap_Unified_Spec_v5.md` (dated 2026-08-17). The files `README.md`, `PROJECT_CONTEXT.md`, and `KIMI_CONTEXT.md` describe an older, simpler cohort-economics prototype and are currently stale. The directory `v5_backup/` holds an earlier partial implementation of the v5 model.

- **Backend:** FastAPI (Python 3.9) with Pydantic v1 models and a pure-Python calculation engine.
- **Frontend:** React 18 + Vite 5 + Recharts 2.x + Zustand 5.x.
- **Data:** JSON-driven configuration; no database.
- **Deployment:** None configured (local dev only).

## 2. Repository layout

```
clp_cost_model/
├── AGENTS.md                      # This file
├── CareerLeap_Unified_Spec_v5.md  # Authoritative v5 product spec
├── PROJECT_CONTEXT.md             # STALE — older cohort-model description
├── KIMI_CONTEXT.md                # STALE — older cohort-model description
├── README.md                      # STALE — older cohort-model description
├── cost_model.py                  # Standalone legacy cohort CLI engine (unused by the app)
├── dashboard-*.png                # UI screenshots
├── backend/                       # FastAPI backend (current app)
│   ├── __init__.py
│   ├── main.py                    # FastAPI routes and CSV export
│   ├── models.py                  # Pydantic v1 input/output schemas
│   ├── engine.py                  # Calculation engine (revenue, costs, break-even, sensitivity)
│   ├── validators.py              # 24 model-validation checks + launch gates
│   ├── tests/
│   │   └── test_fixtures.py       # pytest smoke tests for the 10 questions
│   ├── requirements.txt           # Python dependencies
│   ├── career_tracks.json         # Legacy career-track data (unused by current routes)
│   └── legacy/                    # Older backend modules
│       ├── career_tracks.py
│       └── cost_model.py
├── frontend/                      # React + Vite frontend (current app)
│   ├── index.html
│   ├── package.json
│   ├── package-lock.json
│   ├── vite.config.js             # Dev server + /api proxy
│   ├── README.md                  # Frontend-only notes (also stale)
│   └── src/
│       ├── main.jsx               # React entry point
│       ├── App.jsx                # Orchestrates API calls and layout
│       ├── api.js                 # Fetch wrappers for backend endpoints
│       ├── store.js               # Zustand global state
│       ├── config.js              # Default config mirror + labels
│       ├── index.css              # Global styles
│       └── components/            # Dashboard panels
│           ├── Layout.jsx
│           ├── InputForm.jsx
│           ├── LaunchControlPanel.jsx   # Q10 launch gates (top of page)
│           ├── SummaryCards.jsx         # Q3/Q5/Q6 KPI cards
│           ├── FinancialOutcomePanel.jsx# Q6 revenue bridge + pre-tax profit
│           ├── CompleteCostStatement.jsx# Q1 line-item cost table
│           ├── CostPerParticipantDetail.jsx # Q2 by category / by workstream
│           ├── CostBreakdownChart.jsx
│           ├── WorkstreamToolsTable.jsx
│           ├── PricingSimulator.jsx     # Q4 target-margin slider
│           ├── BreakEvenChart.jsx
│           ├── SensitivityHeatmap.jsx   # Q5 break-even frontier highlight
│           ├── WhatIfSliders.jsx        # Q8 quick what-if sliders
│           ├── ScenarioComparison.jsx   # Q8 save & compare scenarios
│           ├── CashFlowPanel.jsx        # Q7 funding requirement
│           ├── CapacityDashboard.jsx    # Q9 mentor/tool/team capacity
│           ├── TeamCompensationTable.jsx
│           ├── OperationalCostsTable.jsx
│           └── ModelChecks.jsx
└── v5_backup/                     # Archived earlier v5 attempt
    ├── backend/
    └── frontend/
```

## 3. Technology stack

### Backend

- **Language:** Python 3.9 (do **not** use `X | Y` union syntax; use `Optional[X]`, `Union[X, Y]`, `Dict`, `List`).
- **Framework:** FastAPI 0.111.0
- **Server:** Uvicorn 0.30.1 (`uvicorn[standard]`)
- **Validation:** Pydantic 1.x (`pydantic>=1.10,<2`)
- **CORS:** Configured in `backend/main.py` to allow `http://localhost:5173`.
- `backend/.venv` is an in-repo virtualenv whose site-packages contain a few extra packages (httpx, dotenv, email_validator, markdown-it) not listed in `requirements.txt`; only the three pinned dependencies in `requirements.txt` are required by the app.

### Frontend

- **Framework:** React 18.3.1
- **Build tool:** Vite 5.3.1 (ESM project: `"type": "module"`)
- **Charts:** Recharts 2.12.7
- **State:** Zustand 5.0.15
- **No TypeScript:** JSX files with plain JavaScript.
- **Styling:** Plain CSS in `frontend/src/index.css` (no Tailwind in use despite the spec mentioning it).
- **No linter/formatter configured** (no ESLint/Prettier config in the repo).

## 4. Build and run commands

### Backend

```bash
# Create and activate a virtual environment
python3 -m venv backend/.venv
source backend/.venv/bin/activate

# Install dependencies
pip install -r backend/requirements.txt

# Start the development server
uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

API base URL: `http://127.0.0.1:8000`
Interactive docs: `http://127.0.0.1:8000/docs`

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Dev server: `http://localhost:5173`
Vite proxies `/api/*` requests to `http://127.0.0.1:8000` (see `frontend/vite.config.js`).

### Production build (frontend only)

```bash
cd frontend
npm run build    # vite build -> frontend/dist/
npm run preview  # preview the built bundle
```

There are no `lint` or `test` npm scripts; `frontend/package.json` only defines `dev`, `build`, and `preview`.

## 5. API endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Health check |
| GET | `/api/config/defaults` | Return default `PricingScenarioInput` (raw object, not wrapped) |
| POST | `/api/calculate` | Full calculation output (includes `cash_flow` and `capacity`) |
| POST | `/api/calculate/summary` | KPI cards only |
| POST | `/api/calculate/break-even` | Price-surplus curve (prices €500–€1,000 in €25 steps) |
| POST | `/api/calculate/sensitivity` | 2D heatmap data: price €500–€1,000 × cohort size 12–50 (step 4), plus per-size break-even prices |
| POST | `/api/calculate/team` | Internal-team compensation breakdown |
| POST | `/api/calculate/checks` | 24 model validation checks + launch gate status/blockers |
| POST | `/api/calculate/capacity` | Q9 mentor/tool/team capacity result |
| POST | `/api/calculate/cash-flow` | Q7 cash-flow schedule and pre-launch funding requirement |
| POST | `/api/scenarios/compare` | Q8 compare 1–5 scenarios (body: `{scenarios: [...], names: [...]}`) |
| POST | `/api/export/csv` | Download scenario as CSV (`careerleap_pricing_scenario.csv`) |

All POST endpoints accept the full `PricingScenarioInput` JSON body.

## 6. Code organization

### Backend modules

- **`main.py`:** Defines the FastAPI app, CORS middleware, all routes, and CSV export. Keeps route handlers thin; calculation logic is delegated to `engine` and `validators`.
- **`models.py`:** All Pydantic v1 schemas — input configuration (`PricingScenarioInput` with sections `assumptions`, `workstreams`, `tools`, `internal_team`, `operational`, `other_costs`, `pricing`, `launch_gates`, `cash_flow_timing`) and every response model. This is the single source of truth for the JSON shape consumed by the frontend.
- **`engine.py`:** Pure functions for revenue, tools, mentors, internal team, operational costs, other costs, total cost, decisions (incl. launch-gate logic), break-even curve, sensitivity matrix, cash flow, capacity, team compensation, and scenario comparison. All monetary outputs are rounded to 2 decimals via `_r()` (Decimal ROUND_HALF_UP, matching Excel). Module constants `WORKSTREAM_ORDER` (`itsa`, `data`, `marketing`, `product`) and `WORKSTREAM_LABELS` drive iteration order and display names.
- **`validators.py`:** 24 validation checks mirroring the Excel "Checks" sheet, including the Q10 launch-gate checks. Returns `PASS`, `WARN`, or `FAIL` per check plus an overall status, per-gate status, blocking gates, and a `GO`/`HOLD`/`REVIEW` launch-readiness verdict.

### Frontend modules

- **`App.jsx`:** On mount, fetches defaults and runs all calculations. Stores config/results in Zustand. Renders a two-pane layout (CSS class `.layout`): the left pane (`<aside>`, sticky and independently scrollable) holds `InputForm`, the right pane (`<main>`) stacks all dashboard panels — launch control, summary cards, financial outcome, cost statement, cost-per-participant, what-if sliders, charts, scenario comparison, cash flow, capacity, and model checks.
- **`store.js`:** Zustand store with `config`, `result`, `summary`, `checks`, `team`, `breakEven`, `sensitivity`, `loading`, `error`, and an `updateField(path, value)` helper that mutates nested config by dot path (via `structuredClone`).
- **`api.js`:** Thin wrappers around `fetch` for each backend endpoint, plus a bundled `api` object. Uses hard-coded `http://127.0.0.1:8000` as the API base. CSV export fetches the CSV as a blob and triggers a browser download.
- **`config.js`:** Default configuration object that mirrors `PricingScenarioInput` defaults, plus `workstreamLabels` and `toolLabels` maps for UI display.
- **Components:** Each JSX component in `components/` renders one dashboard panel and is driven by props from `App.jsx`.

## 7. Key conventions

### Python

- Use Python 3.9-compatible syntax only.
- Use Pydantic v1 patterns (`BaseModel`, `Field(default=...)`, `.dict()`).
- All currency values are rounded to 2 decimal places before returning to the frontend (keep the `_r()` helper on all returned monetary values when editing `engine.py`).
- Calculation functions are stateless and accept a `PricingScenarioInput` instance.
- USD tool costs are converted to EUR only for aggregated totals; workstream breakdowns show both USD and EUR.

### JavaScript / React

- Functional components with default exports.
- Global state lives in Zustand; local form inputs read from and write to the store via `updateField`.
- Money formatting uses `€${Number(value).toLocaleString('en-IE', ...)}`.
- Percentages are stored as decimals in the backend (e.g., `0.15` for 15%) and multiplied by 100 for display.

### Configuration defaults

Default assumptions and prices are duplicated in two places that must stay in sync:

1. `backend/models.py` (Pydantic defaults)
2. `frontend/src/config.js` (initial UI state)

If you change defaults, update both files. Current pricing defaults: early 6 seats @ €649, standard 10 seats @ €699, installment 4 seats @ €720; 10 participants per workstream (40 total).

## 8. Calculation model (short version)

The engine replicates the v5 Excel workbook:

- **Revenue:** Sum of `seats × price` across early, standard, and installment tiers. Down-payment logic splits immediate vs. deferred receipts (early tier paid in full; standard and installment receipts multiplied by `down_payment_rate`, default 0.30). VAT is calculated only when `vat_treatment == "taxable"`.
- **Tool costs:** Per-workstream monthly tool sum × `tool_access_period_months` × (1 + `contingency_rate`) × participants, converted to EUR at `usd_to_eur_rate`.
- **Mentor costs:** `mentor_hours_per_week × mentor_delivery_weeks × mentor_hourly_rate_eur` per workstream.
- **Internal team:** Founder (Solomon, David, Akua) + volunteer + intern stipends over `internal_team.active_months`.
- **Operational costs:** Notion, Render, Resend, Calendly, AWS, Bitwarden (per-seat or per-month × active months), plus Namecheap (annual).
- **Other costs:** Legal, tax, bookkeeping, payment processing fee, insurance, recruitment, refund reserve, GDPR, certificates, travel, bank charges, accreditation.
- **Decisions:** Cash surplus, margin, break-even price and break-even cohort size (closed form at the current cohort size), target-margin price (closed form, driven by `assumptions.target_cash_surplus_margin`), economics status (`VIABLE` / `REVIEW`), and launch readiness (`GO` / `HOLD` / `REVIEW`). Launch gates: economics VIABLE, confirmed participants ≥ minimum, secured revenue ≥ minimum, and priced seats == planned participants (`HOLD` when the confirmed/secured gates fail, `REVIEW` otherwise). `pre_tax_profit` mirrors `cash_surplus`.
- **Cash flow (Q7):** Per-phase opening/closing balances using `cash_flow_timing` revenue/cost profiles; `pre_launch_funding_required` is the absolute value of the lowest negative closing balance.
- **Capacity (Q9):** Mentor capacity (4 mentors × 6 participants each), free-tier tool limits (Jira Cloud 10 agents, Jira Work Management 10 users), and team bandwidth vs. a 0.75 hrs/week-per-participant recommendation.

Full details, formulas, and expected fixture values are in `CareerLeap_Unified_Spec_v5.md`.

## 9. Testing

A pytest suite lives at `backend/tests/test_fixtures.py` (24 tests). It posts the defaults to the API and locks the fixture values for all 10 business questions (total cost €21,622.25, cost/participant €540.56, break-even price, break-even cohort size at a €688 average price, target-margin price, cash surplus −€7,858.25, cash-flow funding, mentor capacity 24, and the GO/HOLD/REVIEW launch-gate scenarios).

Run it from the repo root:

```bash
backend/.venv/bin/python -m pytest backend/tests/test_fixtures.py -v
```

There is no frontend test setup (no vitest/jest); the frontend is verified with `npm run build` and manual browser checks.

## 10. Security and operational notes

- **Local development only.** There is no authentication, authorization, or production deployment configuration.
- **Hard-coded CORS origin:** `http://localhost:5173`. Update `main.py` if the frontend is served from a different origin in production.
- **No secrets:** The app does not use API keys, database credentials, or environment variables. Do not add a `.env` file unless you also add a secure loading mechanism.
- **CSV export:** Builds the response in memory from the supplied config. No user input is persisted server-side.
- **Legacy files:** `cost_model.py`, `backend/legacy/`, and `backend/career_tracks.json` are not used by the current application. They may be removed or archived if no longer needed.

## 11. Common pitfalls for agents

- Do not trust `README.md`, `PROJECT_CONTEXT.md`, or `KIMI_CONTEXT.md` as the source of current behavior; refer to `CareerLeap_Unified_Spec_v5.md` and the actual code instead.
- Any change to Pydantic models usually requires a matching change to `frontend/src/config.js` and sometimes to the UI components that consume the response.
- Percent fields are decimals in the backend (e.g., `0.023`) but displayed as percentages in the UI.
- The "Other costs" total is tracked separately and is **not** included in `TotalCostResult.total` (which sums only tools + mentors + internal team + operational, = €21,622.25 at defaults). The payment-fee/refund-reserve terms are instead reflected in the break-even/target-price algebra via the `(1 - payment_processing_fee_rate)` divisor.
- A few figures in `kimi_prompt_10_business_questions.md` do not reconcile with its own formulas at the stated defaults; the code follows the formulas. Documented in the header of `backend/tests/test_fixtures.py`: break-even price rounds to €553.28 (prompt says €553.27), target-margin price (5%) is €582.40 (prompt says €801.77), and pre-launch funding is €7,858.25 from the spec's timing profiles (prompt says €1,170 "from Excel"). The €688 average-price fixtures assume all 40 seats are priced; the defaults only price 20 of 40 seats (average €344.10), which also trips the seat-reconciliation gate.
- `BreakEvenResponse` has no `current_surplus` field; it carries `current_model` (participants, average price, total cost, surplus, margin), the `curve`, `cash_break_even_price`, `target_margin_price`, and `gap_current_vs_break_even` (current average price minus break-even price).
- `models.py` quirk: `InternSpec.monthly` has a class-level default of `218.72` but the `InternalTeamConfig` default factory overrides it to `218.60`. The effective default is `218.60`.
- `frontend/src/api.js` uses a hard-coded API base (`http://127.0.0.1:8000`) rather than the Vite proxy, so the frontend talks to the backend cross-origin; both the backend CORS setting and the API base must agree.
- When editing `engine.py`, keep the `_r()` rounding helper on all returned monetary values.

## 12. Suggested next steps (if asked)

- Update `README.md`, `PROJECT_CONTEXT.md`, and `KIMI_CONTEXT.md` to match the current v5 implementation, or delete them and point readers to `CareerLeap_Unified_Spec_v5.md`.
- Add a production-ready deployment configuration (Docker, Gunicorn + Uvicorn, static frontend serving).
- Add form validation and user-facing error boundaries in the frontend.
- Add frontend tests (vitest) for the panel components.
