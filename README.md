# CareerLeap Pricing Dashboard

An interactive web dashboard that replicates the economics of the **CareerLeap_Pricing_Broad.xlsx** workbook. Edit assumptions about cohort size, per-workstream tooling, mentor hours, team stipends, operational and other costs, and seat pricing — the dashboard recalculates revenue, costs, margins, break-even prices, cash-flow timing, capacity, and launch readiness in real time.

- **Backend:** FastAPI (Python 3.9) + Pydantic v1, pure-Python calculation engine
- **Frontend:** React 18 + Vite 5 + Recharts + Zustand
- **Data:** JSON-driven configuration, no database
- The authoritative product spec is [`CareerLeap_Unified_Spec_v5.md`](CareerLeap_Unified_Spec_v5.md)

## What it answers (10 business questions)

| # | Question | Where |
|---|----------|-------|
| 1 | What is the complete cost of running one cohort? | Complete Cost Statement (every line item, EUR + USD) |
| 2 | What is the actual cost per participant? | Cost Per Participant panel — by category and by workstream |
| 3 | What minimum price is required to break even? | Summary card + Break-Even chart, live distance-to-break-even |
| 4 | What price achieves our target margin? | Pricing Simulator — target-margin slider (0–50%) |
| 5 | How many paying participants are required to break even? | Summary card + highlighted break-even frontier on the heatmap |
| 6 | What revenue, surplus, pre-tax profit and margin will the cohort generate? | Financial Outcome panel with revenue bridge |
| 7 | How much cash is required before launch, and when could shortages occur? | Cash Flow panel — pre-launch funding requirement and lowest balance |
| 8 | What happens if numbers, prices, duration or costs change? | What-If Sliders + Scenario Comparison (save & compare A/B/C) |
| 9 | Can mentors, team and licences support the cohort size? | Capacity Dashboard — mentor/tool/team status (OK/WARNING/FAIL) |
| 10 | Should the cohort launch: GO, HOLD or REVIEW? | Launch Control Panel — 5 gates + confirmed participants & secured revenue inputs |

## Quick start

Prerequisites: Python 3.9+, Node 18+.

```bash
# 1. Backend (from the repo root)
python3 -m venv backend/.venv
source backend/.venv/bin/activate
pip install -r backend/requirements.txt
uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000

# 2. Frontend (in a second terminal)
cd frontend
npm install
npm run dev
```

Then open **http://localhost:5173**. Parameters live in the left pane; the dashboard fills the right. Use **Recalculate** after editing inputs — sliders and launch-gate fields recalculate automatically.

Other useful commands:

```bash
cd frontend && npm run build     # production build -> dist/
backend/.venv/bin/python -m pytest backend/tests/test_fixtures.py -v   # 25 fixture tests
```

## How the model works (short version)

- **Revenue:** `seats × price` across early / standard / installment tiers, with down-payment splitting (early paid in full; other tiers × 30% immediate). VAT only when `vat_treatment == "taxable"`.
- **Costs:** tools (per-workstream USD matrix × access months × (1 + contingency), converted at the USD→EUR rate), mentors (hours/week × weeks × rate), internal team stipends, operational subscriptions, and revenue-dependent "other" costs.
- **Headline numbers at the default config:** total cost **€21,622.25** (excl. other costs, which are tracked separately), cost/participant **€540.56**, break-even price **€553.28**, cash surplus **−€7,858.25** (margin −57.1%), mentor capacity 24 → the default plan does **not** launch (status: HOLD).
- **Launch gates (Q10):** economics VIABLE (margin ≥ target), confirmed participants ≥ minimum (16), secured revenue ≥ minimum (€10,000), all model checks pass, priced seats == planned participants → **GO** / **HOLD** / **REVIEW**.
- The backend test suite (`backend/tests/test_fixtures.py`) locks these fixture values; see its header for notes on a few prompt/Excel figures that don't reconcile with the formulas (target-margin price, pre-launch funding).

## API overview

All POST endpoints accept the full `PricingScenarioInput` JSON body. Base URL: `http://127.0.0.1:8000` (interactive docs at `/docs`).

| Endpoint | Description |
|----------|-------------|
| `GET /api/config/defaults` | Default scenario input |
| `POST /api/calculate` | Full calculation (revenue, costs, decisions, cash flow, capacity) |
| `POST /api/calculate/summary` | KPI cards |
| `POST /api/calculate/break-even` | Price–surplus curve + break-even/target prices |
| `POST /api/calculate/sensitivity` | Price × cohort-size margin grid + break-even frontier |
| `POST /api/calculate/team` | Internal-team compensation |
| `POST /api/calculate/checks` | 24 model checks + launch gates/blockers |
| `POST /api/calculate/capacity` | Mentor/tool/team capacity |
| `POST /api/calculate/cash-flow` | Cash schedule + pre-launch funding need |
| `POST /api/scenarios/compare` | Compare 1–5 scenarios |
| `POST /api/export/csv` | Download the scenario as CSV |

## Repository layout

```
backend/            FastAPI app: main.py (routes), models.py (schemas),
                    engine.py (calculations), validators.py (checks), tests/
frontend/           React app: src/App.jsx (two-pane layout), src/components/ (panels)
CareerLeap_Unified_Spec_v5.md   Authoritative spec
AGENTS.md           Detailed agent/developer guide
v5_backup/          Archived earlier v5 attempt
cost_model.py       Standalone legacy cohort CLI engine (unused by the app)
```

> **Note:** `PROJECT_CONTEXT.md` and `KIMI_CONTEXT.md` describe an older prototype and are stale — refer to this README, `AGENTS.md`, and the spec instead.
