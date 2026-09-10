# CareerLeap Business Model Dashboard — Unified Specification
## Fused from Project Context v2.0 + Excel Pricing Model v4.0

**Version:** 5.0  
**Date:** 2026-08-17  
**Purpose:** Single source of truth for Kimi Code to expand the full-stack dashboard  
**Stack:** FastAPI (Python 3.9) + React 18 + Vite 5 + Recharts 2.x

---

## 1. Executive Summary

Build a production-grade full-stack dashboard that lets CareerLeap founders model cohort economics in real time. The dashboard must replicate **all sheets** from the Excel v4.0 pricing model (Simulator, Inputs, Tools, Calculations, Scenarios, Sensitivity, Cash Flow, Break-even, Checks) as interactive web views, while preserving the existing career-track tool breakdown from the v2.0 project context.

**Key constraint:** The backend must remain Python 3.9-compatible (no `X | Y` union syntax). Use `Optional[X]` and `Union[X, Y]` from `typing`.

---

## 2. Architecture

```
clp_cost_model/
├── README.md
├── cost_model.py                    # CLI engine (standalone, do not modify)
├── backend/
│   ├── __init__.py
│   ├── main.py                      # FastAPI app with all routes
│   ├── models.py                    # Pydantic v1 schemas (Python 3.9)
│   ├── engine.py                    # CohortModel + AnnualProjection + Sensitivity
│   ├── cashflow.py                  # CashFlowModel with timing profiles
│   ├── breakeven.py                 # BreakEvenModel with price solver
│   ├── scenarios.py                 # ScenarioGenerator (Conservative/Base/Growth/Custom)
│   ├── checks.py                    # ModelChecks validator
│   ├── career_tracks.py             # Career track loader
│   ├── career_tracks.json           # Track data (tools, prices, skills, sources)
│   ├── team_roster.json             # Internal team + mentor config
│   ├── pricing_tiers.json           # Seat mix defaults
│   └── requirements.txt             # fastapi, uvicorn, pydantic, python-multipart
└── frontend/
    ├── package.json
    ├── vite.config.js               # Proxy /api → localhost:8000
    ├── index.html
    └── src/
        ├── main.jsx
        ├── App.jsx
        ├── api.js
        ├── index.css
        ├── store.js                   # Zustand or React Context for global state
        └── components/
            ├── Layout.jsx             # Sidebar nav + main content area
            ├── SimulatorPanel.jsx     # Central control panel (replaces Excel "Simulator")
            ├── InputsPanel.jsx        # Detailed inputs (replaces Excel "Inputs")
            ├── ToolsPanel.jsx         # Tool cost builder (replaces Excel "Tools")
            ├── CalculationsPanel.jsx  # Transparent calc walkthrough
            ├── ScenariosPanel.jsx     # 4-scenario comparison (Conservative/Base/Growth/Custom)
            ├── SensitivityPanel.jsx   # Two-variable heatmap + line charts
            ├── CashFlowPanel.jsx      # Monthly cash flow table + chart
            ├── BreakEvenPanel.jsx     # Price-surplus curve + solver
            ├── ChecksPanel.jsx        # Model validation dashboard
            ├── KPICards.jsx           # Top-level metrics row
            ├── CostBreakdownChart.jsx # Revenue vs costs bar chart
            ├── CareerTrackTools.jsx   # Per-track tool breakdown
            ├── PricingTiersTable.jsx  # Recommended pricing tiers
            ├── AnnualProjection.jsx   # Annual summary cards
            └── SensitivityCharts.jsx  # Fee & cohort size line charts
```

---

## 3. Backend API Specification

### 3.1 Health & Defaults

```
GET  /api/health           → {"status": "ok"}
GET  /api/defaults         → CohortConfigInput with all default values
GET  /api/career-tracks    → List[CareerTrackOutput]
GET  /api/team-roster      → TeamRoster (internal team + mentor assumptions)
GET  /api/pricing-tiers    → PricingTierDefaults (seat mix, prices)
```

### 3.2 Core Calculation

```
POST /api/calculate
  Body: CohortConfigInput
  Response: CalculateResponse
```

### 3.3 Advanced Endpoints

```
POST /api/scenarios        → ScenariosResponse (Conservative/Base/Growth/Custom)
POST /api/sensitivity      → SensitivityResponse (fee × cohort_size heatmap)
POST /api/cash-flow        → CashFlowResponse (monthly schedule)
POST /api/break-even       → BreakEvenResponse (price curve + exact solver)
POST /api/checks           → ChecksResponse (all model validations)
POST /api/export/csv       → CSV download (scenario grid)
```

---

## 4. Data Models (Pydantic v1, Python 3.9)

### 4.1 CohortConfigInput

```python
from typing import Optional, List
from pydantic import BaseModel, Field

class SeatMix(BaseModel):
    early_payment_seats: int = 6
    early_payment_price: float = 649.0
    standard_payment_seats: int = 10
    standard_payment_price: float = 699.0
    installment_seats: int = 4
    installment_price: float = 720.0

class WorkstreamConfig(BaseModel):
    it_systems_admin: int = 5
    data_bi_ai: int = 5
    product_project_ops: int = 5
    digital_marketing_growth: int = 5

class CohortConfigInput(BaseModel):
    # Core simulation controls
    workstreams: WorkstreamConfig = WorkstreamConfig()
    seat_mix: SeatMix = SeatMix()

    # Programme timing
    delivery_weeks: int = 12
    m365_access_before_launch_weeks: int = 1
    extension_wrapup_weeks: int = 1
    m365_billing_months: int = 4

    # Financial controls
    vat_applies: bool = True
    vat_rate: float = 0.19
    payment_processing_fee_rate: float = 0.025
    external_cost_contingency_rate: float = 0.15
    target_cash_surplus_margin: float = 0.05

    # Launch gates
    minimum_total_participants: int = 16
    minimum_per_workstream: int = 4
    minimum_secured_net_revenue: float = 10000.0
    secured_net_revenue_to_date: float = 0.0
    internal_team_workload_multiplier: float = 1.0
    participant_count_workload_review_threshold: int = 24

    # Mentor assumptions
    mentor_contact_hours_per_week: float = 2.0
    mentor_prep_hours_per_week: float = 2.0
    mentor_setup_hours: float = 8.0
    mentor_hourly_rate: float = 20.0
    mentor_capacity_per_mentor: int = 6

    # Internal team (loaded from team_roster.json, editable here)
    internal_team_payments: List[dict] = []  # populated from JSON

    # Other external costs
    other_external_costs: List[dict] = []  # accounting, legal, insurance, etc.

    # Career track (for tool cost override)
    career_track: str = "it_infrastructure"
    tool_cost_per_user_per_month: Optional[float] = None  # auto-derived from track if null
    fixed_tool_cost_per_month: Optional[float] = None     # auto-derived from track if null

    # Legacy fields (keep for backward compatibility)
    participant_fee: Optional[float] = None  # DEPRECATED: use seat_mix blended average
    cohort_size: Optional[int] = None        # DEPRECATED: use workstreams total
    duration_months: Optional[int] = None    # DEPRECATED: use delivery_weeks
    num_leads: Optional[int] = None          # DEPRECATED: derived from workstreams
    stipend_per_lead: Optional[float] = None # DEPRECATED: use mentor hourly model
    overhead_per_participant: Optional[float] = 150.0
    placement_bonus_per_lead: float = 0.0
    no_show_rate: float = 0.05
    refund_rate: float = 0.03
```

### 4.2 CalculateResponse

```python
class RevenueBreakdown(BaseModel):
    participant_gross_receipts: float
    vat_payable: float
    net_programme_revenue: float
    average_gross_price_per_participant: float
    average_net_price_per_participant: float

class CostBreakdown(BaseModel):
    mentor_cost: float
    m365_licences: float
    other_tools: float
    internal_team_payments: float
    other_external_costs: float
    payment_processing_fees: float
    contingency_reserve: float
    total_cohort_cash_cost: float
    cash_cost_per_participant: float

class DecisionOutputs(BaseModel):
    cash_surplus: float
    cash_surplus_margin: float
    cash_break_even_average_price: float
    target_margin_average_price: float
    price_gap_to_target: float
    minimum_additional_cash_buffer: float
    projected_economics_status: str   # "VIABLE" or "REVIEW"
    actual_launch_readiness: str      # "GO" or "HOLD"

class CalculateResponse(BaseModel):
    config: CohortConfigInput
    revenue: RevenueBreakdown
    costs: CostBreakdown
    decisions: DecisionOutputs
    pricing_tiers: List[PricingTier]
    sensitivity: SensitivityData
    annual_projection: AnnualProjectionData
    career_track: Optional[CareerTrackOutput]
    tool_breakdown: List[ToolBreakdownItem]
```

### 4.3 Scenario Response

```python
class ScenarioResult(BaseModel):
    name: str
    participants: int
    net_revenue: float
    cash_cost: float
    cash_surplus: float
    cash_surplus_margin: float
    cash_cost_per_participant: float
    average_gross_price: float
    target_margin_price: float
    price_gap_to_target: float
    status: str  # "VIABLE" or "REVIEW"

class ScenariosResponse(BaseModel):
    conservative: ScenarioResult
    base: ScenarioResult
    growth: ScenarioResult
    custom: ScenarioResult
    custom_name: str = "Custom"
```

### 4.4 Sensitivity Response

```python
class SensitivityCell(BaseModel):
    participants: int
    average_price: float
    cash_surplus: float
    cash_surplus_margin: float
    status: str  # "surplus" or "deficit"

class SensitivityResponse(BaseModel):
    current_reference: dict
    grid: List[List[SensitivityCell]]  # 2D matrix
    break_even_prices: List[dict]  # per cohort size
    controls: dict  # starting_price, price_step, starting_participants, participant_step
```

### 4.5 Cash Flow Response

```python
class CashFlowMonth(BaseModel):
    phase: str  # "Pre-launch", "Month 1", "Month 2", "Month 3", "Extension"
    net_revenue_collected: float
    cash_costs_paid: float
    net_cash_movement: float
    opening_balance: float
    closing_balance: float

class CashFlowResponse(BaseModel):
    timing_assumptions: dict  # revenue_profile, cost_profile
    monthly_schedule: List[CashFlowMonth]
    minimum_funding_buffer: float
    lowest_projected_balance: float
    ending_balance: float
```

### 4.6 Break-Even Response

```python
class BreakEvenPoint(BaseModel):
    average_gross_price: float
    gross_receipts: float
    net_programme_revenue: float
    total_cohort_cash_cost: float
    cash_surplus: float
    cash_surplus_margin: float

class BreakEvenResponse(BaseModel):
    current_model: dict
    curve: List[BreakEvenPoint]
    cash_break_even_price: float
    target_margin_price: float
    gap_current_vs_break_even: float
    chart_controls: dict  # starting_price, price_step
```

### 4.7 Checks Response

```python
class ModelCheck(BaseModel):
    name: str
    actual: str
    expected: str
    difference: str
    tolerance: str
    status: str  # "OK" or "FAIL"
    where_to_fix: str
    why_it_matters: str

class ChecksResponse(BaseModel):
    checks: List[ModelCheck]
    overall_status: str  # "PASS" or "FAIL"
    launch_readiness: str  # "GO" or "HOLD"
```

---

## 5. Business Logic Specification

### 5.1 Revenue Calculation (from Excel v4.0)

```
participant_gross_receipts = Σ(seat_type_seats × seat_type_price)
  = early_seats × early_price + standard_seats × standard_price + installment_seats × installment_price

vat_payable = participant_gross_receipts × vat_rate / (1 + vat_rate)   [if vat_applies]
            = 0                                                        [if not vat_applies]

net_programme_revenue = participant_gross_receipts - vat_payable
```

**Default seat mix:**
- Early payment: 6 seats @ €649
- Standard payment: 10 seats @ €699
- Installment plan: 4 seats @ €720
- Total: 20 participants, blended average €688.20

### 5.2 Cost Calculation (from Excel v4.0)

#### 5.2.1 Mentor Costs

```
required_mentors = ceil(workstream_participants / mentor_capacity_per_mentor) per active workstream
                 = typically 4 mentors (1 per workstream) at 20 participants

hours_per_mentor_per_week = mentor_contact_hours_per_week + mentor_prep_hours_per_week
                          = 2 + 2 = 4 hours/week

total_mentor_hours = (required_mentors × hours_per_mentor_per_week × delivery_weeks)
                   + (required_mentors × mentor_setup_hours)
                   = (4 × 4 × 12) + (4 × 8) = 192 + 32 = 224 hours

mentor_cash_cost = total_mentor_hours × mentor_hourly_rate
                 = 224 × €20 = €4,480
```

#### 5.2.2 M365 Licences

```
total_m365_accounts = participants + mentors + internal_team_members + extra_accounts
                    = 20 + 4 + 6 + 0 = 30 accounts

m365_billing_months = delivery_weeks/4 + m365_access_before_launch_weeks/4 + extension_wrapup_weeks/4
                    = 3 + 0.25 + 0.25 = 3.5 → rounded up to 4 months

m365_licence_cost = total_m365_accounts × m365_billing_months × m365_price_per_account_per_month
                  = 30 × 4 × €7.28 = €873.60
```

#### 5.2.3 Other Tools

Loaded from `career_tracks.json` + `Tools` sheet logic:
- Shared tools: €100 (storage/domain allowance) + M365
- IT Systems Admin: €400 (training tenant €150 + Azure credits €100 + VM fallback €150 + Jira €0)
- Data, BI & AI: €75 (cloud DB credits)
- Product/Operations: €0 (Jira/Confluence free)
- Digital Marketing: €300 (controlled campaign experiment)
- **Total other tools: €875**

#### 5.2.4 Internal Team Payments

Loaded from `team_roster.json`:

| Member | Weekly Hrs | Weeks | Rate | Payment | M365? |
|--------|-----------|-------|------|---------|-------|
| Solomon | 4.5 | 12 | €20 | €1,080 | Yes |
| David | 3.5 | 12 | €20 | €840 | Yes |
| Akua | 3.5 | 12 | €20 | €840 | Yes |
| Intern | 4.0 | 12 | €15 | €720 | Yes |
| Volunteer 1 | 2.0 | 12 | €15 | €360 | Yes |
| Volunteer 2 | 2.0 | 12 | €15 | €360 | Yes |
| **Total** | | | | **€4,200** | **6 accounts** |

Formula: `payment = weekly_hours × weeks × hourly_rate × internal_team_workload_multiplier`

#### 5.2.5 Other External Costs

| Item | Included? | Cost |
|------|-----------|------|
| Accounting & VAT consultation | Yes | €350 |
| Legal review (enrolment, refunds, GDPR) | Yes | €500 |
| Business liability insurance | No | €0 |
| Paid recruitment advertising | No | €0 |
| Venue/travel logistics | No | €0 |
| **Total included** | | **€850** |

#### 5.2.6 Payment Processing Fees

```
payment_processing_fees = participant_gross_receipts × payment_processing_fee_rate
                        = €13,764 × 0.025 = €344.10
```

#### 5.2.7 Contingency Reserve

```
external_cash_cost_before_contingency = mentor_cost + tools + other_external + payment_fees
                                      = €4,480 + €1,748.60 + €850 + €344.10 = €7,422.70

contingency_reserve = external_cash_cost_before_contingency × external_cost_contingency_rate
                    = €7,422.70 × 0.15 = €1,113.41
```

**Note:** Internal-team payments are EXCLUDED from contingency.

#### 5.2.8 Total Cohort Cash Cost

```
total_cohort_cash_cost = external_cash_cost_before_contingency + contingency_reserve + internal_team_payments
                       = €7,422.70 + €1,113.41 + €4,200 = €12,736.11
```

### 5.3 Decision Outputs

```
cash_surplus = net_programme_revenue - total_cohort_cash_cost
cash_surplus_margin = cash_surplus / net_programme_revenue
cash_cost_per_participant = total_cohort_cash_cost / planned_participants
net_revenue_per_participant = net_programme_revenue / planned_participants
```

#### Price Solver (Break-even & Target Margin)

```
vat_gross_up_divisor = 1 + vat_rate  [if vat_applies] else 1.0
target_revenue_retained = 1 - target_cash_surplus_margin
required_price_denominator = target_revenue_retained - payment_processing_fee_rate

external_cost_excl_payment_and_contingency = mentor_cost + tools + other_external_costs
required_price_numerator = (external_cost_excl_payment_and_contingency × (1 + external_cost_contingency_rate)
                            + internal_team_payments)

required_total_gross_receipts = required_price_numerator / required_price_denominator
cash_break_even_average_price = required_total_gross_receipts / planned_participants / vat_gross_up_divisor

target_margin_numerator = required_price_numerator / target_revenue_retained
target_margin_total_gross = target_margin_numerator / required_price_denominator
target_margin_average_price = target_margin_total_gross / planned_participants / vat_gross_up_divisor
```

### 5.4 Scenarios (from Excel "Scenarios" sheet)

| Scenario | Participants | Price Multiplier | Workload Multiplier | M365 Extension | Status |
|----------|-------------|------------------|---------------------|----------------|--------|
| Conservative | 16 (4 per stream) | 0.95× | 1× | 1 week | REVIEW |
| Base | 20 (5 per stream) | 1.00× | 1× | 1 week | REVIEW |
| Growth | 40 (10 per stream) | 1.05× | 2× | 2 weeks | REVIEW |
| Custom | 24 (6 per stream) | 1.10× | 1× | 1 week | VIABLE |

Each scenario recalculates:
- Revenue (with VAT and payment fees)
- Mentor count (scales with capacity)
- M365 accounts and billing months
- Tool costs (fixed + variable)
- Internal team payments (scales with workload multiplier)
- Contingency
- Cash surplus and margin

### 5.5 Sensitivity (from Excel "Sensitivity" sheet)

Two-variable decision table:
- **X-axis:** Average participant price (€500–€1,000, step €25)
- **Y-axis:** Cohort size (12–40, step 4)
- **Cell value:** Cash surplus (€)
- **Color coding:** Green = surplus, Red = deficit

Also include break-even price per cohort size as a derived column.

### 5.6 Cash Flow (from Excel "Cash Flow" sheet)

Timing profiles (must sum to 1.0):
- **Revenue collection:** Pre-launch 40%, Month 1 25%, Month 2 20%, Month 3 10%, Extension 5%
- **Cost payment:** Pre-launch 25%, Month 1 25%, Month 2 20%, Month 3 20%, Extension 10%

Monthly schedule:
```
net_revenue_collected = net_programme_revenue × revenue_profile[phase]
cash_costs_paid = total_cohort_cash_cost × cost_profile[phase]
net_cash_movement = net_revenue_collected - cash_costs_paid
opening_balance = previous_closing_balance (0 for pre-launch)
closing_balance = opening_balance + net_cash_movement
```

Outputs:
- Minimum additional funding buffer = |lowest_negative_closing_balance|
- Lowest projected cash balance
- Ending cash balance = cohort cash surplus

### 5.7 Break-Even Curve (from Excel "Break-even" sheet)

Generate a curve of 21 points:
- Average gross price: €500 to €1,000 in €25 steps
- For each price, recalculate gross receipts, net revenue, cash cost, surplus
- Plot cash surplus vs price
- Mark cash break-even line at €0
- Mark current model position
- Mark target-margin price

### 5.8 Model Checks (from Excel "Checks & Guide" sheet)

21 validation checks that must all pass:

| # | Check | Tolerance | Status |
|---|-------|-----------|--------|
| 1 | Planned pricing seats = planned participants | 0 | OK |
| 2 | Confirmed ≤ planned participants | 0 | OK |
| 3 | Every active workstream has ≥1 mentor | 0 | OK |
| 4 | Mentor hours and rate are positive | 0 | OK |
| 5 | M365 account count reconciles | 0 | OK |
| 6 | M365 billing months cover all access weeks | 0 | OK |
| 7 | Tool detail = tool summary | 0.01 | OK |
| 8 | Revenue total = revenue components | 0.01 | OK |
| 9 | Cash cost = cost components | 0.01 | OK |
| 10 | Cash surplus = revenue - cash cost | 0.01 | OK |
| 11 | Base scenario participants = Inputs | 0 | OK |
| 12 | Base scenario revenue = Calculations | 0.01 | OK |
| 13 | Base scenario cash cost = Calculations | 0.01 | OK |
| 14 | Workstream minimum = global control | 0 | OK |
| 15 | Cash break-even produces ≈€0 surplus | 0.01 | OK |
| 16 | Custom scenario seats = participants | 0 | OK |
| 17 | Revenue timing profile totals 100% | 0.0001 | OK |
| 18 | Cost timing profile totals 100% | 0.0001 | OK |
| 19 | Cash-flow revenue = Calculations | 0.01 | OK |
| 20 | Cash-flow cost = Calculations | 0.01 | OK |
| 21 | Closing cash = opening + cohort surplus | 0.01 | OK |

**Overall status:** PASS if all OK, FAIL if any FAIL.  
**Launch readiness:** GO only if PASS + confirmed participants ≥ minimum + secured net revenue ≥ minimum.

---

## 6. Career Tracks Data (from Project Context v2.0)

Keep the existing `career_tracks.json` structure with these 3 tracks:

### 6.1 IT Infrastructure & Support
- **Cost per user:** €12.00/mo
- **Tools:** Google Workspace (€6), Google Admin Console (bundled), Jira Cloud (free), 1Password (€6), Slack (free)
- **Skills:** Workspace admin, IAM, onboarding/offboarding, ticketing, secrets management, Slack governance, OAuth, 2FA

### 6.2 Data Analytics & Engineering
- **Cost per user:** €1.00/mo
- **Tools:** PostgreSQL (free), DuckDB (free), dbt Core (free), MotherDuck (free), Metabase (free), GitHub Actions (free), Railway/DigitalOcean (€15/mo shared)
- **Skills:** SQL, data cleaning, DuckDB OLAP, dbt modeling, Metabase BI, Python, Git CI/CD, ETL

### 6.3 Digital Marketing & Content
- **Cost per user:** €1.80/mo
- **Tools:** Webflow (€18/mo), Ghost (€9/mo), Canva (free), Figma (free), Notion (free), Beehiiv (free), GA4 (free), Search Console (free)
- **Skills:** No-code web building, content strategy, SEO/SEM, social media, campaigns, GA4 analytics, copywriting, newsletter growth

Each tool must include:
```json
{
  "name": "...",
  "category": "...",
  "billing_model": "per_user_per_month | fixed_monthly | free_tier | open_source | bundled",
  "cost_per_user_per_month": 0.0,
  "cost_total_for_cohort": 0.0,
  "free_tier_available": true,
  "free_tier_limit": "...",
  "why_chosen": "...",
  "source_url": "https://...",
  "last_verified": "2026-08-15"
}
```

---

## 7. Frontend Component Specification

### 7.1 Layout

- **Sidebar navigation:** Simulator | Inputs | Tools | Calculations | Scenarios | Sensitivity | Cash Flow | Break-even | Checks
- **Top bar:** CareerLeap logo, cohort name/ID, last saved timestamp, export buttons (CSV, PDF)
- **Main content:** Scrollable panel with cards, charts, and tables

### 7.2 Simulator Panel (Central Control)

Replicate the Excel "Simulator" sheet:
- **Workstream grid:** 4 rows (IT, Data, Ops, Marketing) with Planned / Confirmed / Place Type / Seats / Gross Price
- **Seat mix editor:** Early (6 @ €649), Standard (10 @ €699), Installment (4 @ €720) — all editable
- **Programme controls:** Delivery weeks, M365 access weeks, extension weeks
- **Financial controls:** VAT toggle + rate, payment fee %, contingency %, target margin %
- **Launch gates:** Min participants, min per workstream, min secured revenue, secured revenue to date
- **Live decision outputs:** Planned participants, current average price, cash-surplus margin, net revenue, cash cost, cash surplus, projected economics status, actual launch readiness
- **Decision guidance:** Cash break-even price, target-margin price, recommended pricing action, minimum additional cash buffer
- **Cost composition table:** Mentors, M365, other tools, internal team, other external, payment fees, contingency

### 7.3 Inputs Panel

Replicate Excel "Inputs" sheet:
- **Cohort structure table:** Workstream, planned, confirmed, minimum, capacity per mentor, required mentors, status
- **Pricing and seat mix table:** Place type, planned seats, price per seat, treatment, cash receipts, who pays
- **Financial controls table:** Control, value, unit, model use, owner, input basis, decision note, update frequency
- **Mentor assumptions table:** Contact hrs/week, prep hrs/week, setup hrs, hourly rate, total hours, total cost
- **Internal team table:** Member, include?, weekly hrs, weeks, rate, calculated payment, M365?, contribution
- **Other external costs table:** Item, include?, budget, included cost, priority, explanation

### 7.4 Tools Panel

Replicate Excel "Tools" sheet:
- **Tool grid:** Scope, Tool/Service, Include? (toggle), Cost basis, Unit cost, Billing periods, Quantity, Included cost, Source ID, Delivery note, Owner
- **Cost summary by scope:** Shared, IT, Data, Operations, Marketing — fixed cost, variable rate, cohort total
- **Source references table:** ID, Input/Limit, Value, Source, URL, Date, Owner

### 7.5 Calculations Panel

Replicate Excel "Calculations" sheet as a transparent walkthrough:
- Revenue calculation step-by-step (paid places, gross receipts, VAT, net revenue)
- Cash-cost calculation step-by-step (mentors, tools, internal team, external, fees, contingency, total)
- Decision outputs (surplus, margin, cost per participant, break-even price, target price)
- Required-price formula bridge (VAT divisor, retained revenue, denominator, numerator, required gross receipts)

### 7.6 Scenarios Panel

Replicate Excel "Scenarios" sheet:
- 4 scenario cards side-by-side: Conservative | Base | Growth | Custom
- Each card shows: participants per workstream, seat mix, price multiplier, workload multiplier, M365 extension
- Output row: net revenue, cash cost, cash surplus, margin %, cost per participant, average price, target price, status
- Custom scenario is fully editable

### 7.7 Sensitivity Panel

Replicate Excel "Sensitivity" sheet:
- **Heatmap:** X-axis = average price (€500–€1000), Y-axis = participants (12–40), cell color = surplus/deficit
- **Break-even price table:** Participants, per workstream, mentors, M365 accounts, fixed tools, variable tools, external cost, internal payment
- **Controls:** Starting price, price step, starting participants, participant step

### 7.8 Cash Flow Panel

Replicate Excel "Cash Flow" sheet:
- **Timing assumption editors:** Revenue collection profile (% per phase), cost payment profile (% per phase)
- **Monthly schedule table:** Phase, Net revenue, Cash costs, Net movement, Opening balance, Closing balance
- **Cash chart:** Line chart showing opening balance, closing balance, and zero line across phases
- **Outputs:** Revenue profile total, minimum funding buffer, lowest balance, ending balance

### 7.9 Break-Even Panel

Replicate Excel "Break-even" sheet:
- **Current model snapshot:** Planned participants, current average price, current surplus, projected economics
- **Curve chart:** X-axis = average gross price (€500–€1000), Y-axis = cash surplus, line = surplus curve, horizontal line = €0 break-even, vertical markers = current price, break-even price, target-margin price
- **Data table:** Price, gross receipts, net revenue, cash cost, surplus, margin, break-even line

### 7.10 Checks Panel

Replicate Excel "Checks & Guide" sheet:
- **Check table:** 21 rows with check name, actual, expected, difference, tolerance, status (green OK / red FAIL), where to fix, why it matters
- **Overall status banner:** PASS (green) or FAIL (red)
- **Launch readiness banner:** GO (green) or HOLD (red/amber)
- **Definitions accordion:** Net programme revenue, total cohort cash cost, cash surplus, break-even price, launch readiness

---

## 8. State Management

Use **Zustand** or React Context to maintain global state:

```javascript
// store.js
const useStore = create((set, get) => ({
  config: defaultConfig,           // CohortConfigInput
  result: null,                    // CalculateResponse
  activePanel: 'simulator',        // Current view
  lastSaved: null,                 // Timestamp
  isLoading: false,                // API call in progress

  updateConfig: (path, value) => set(state => ({ config: setPath(state.config, path, value) })),
  calculate: async () => {
    set({ isLoading: true });
    const res = await api.calculate(get().config);
    set({ result: res, lastSaved: new Date().toISOString(), isLoading: false });
  },
  exportCSV: () => api.exportCSV(get().config),
}));
```

All panels read from the same `config` and `result` objects. Changes in Simulator auto-update Inputs, and vice versa.

---

## 9. API Integration (frontend)

```javascript
// api.js
const API_BASE = '/api';

export const api = {
  calculate: (config) => fetch(`${API_BASE}/calculate`, {
    method: 'POST', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(config)
  }).then(r => r.json()),

  getScenarios: (config) => fetch(`${API_BASE}/scenarios`, {
    method: 'POST', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(config)
  }).then(r => r.json()),

  getSensitivity: (config) => fetch(`${API_BASE}/sensitivity`, {
    method: 'POST', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(config)
  }).then(r => r.json()),

  getCashFlow: (config) => fetch(`${API_BASE}/cash-flow`, {
    method: 'POST', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(config)
  }).then(r => r.json()),

  getBreakEven: (config) => fetch(`${API_BASE}/break-even`, {
    method: 'POST', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(config)
  }).then(r => r.json()),

  getChecks: (config) => fetch(`${API_BASE}/checks`, {
    method: 'POST', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(config)
  }).then(r => r.json()),

  exportCSV: (config) => fetch(`${API_BASE}/export/csv`, {
    method: 'POST', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(config)
  }).then(r => r.blob()),
};
```

---

## 10. Default Values (Base Case)

These must match the Excel v4.0 base case exactly:

```yaml
participants:
  it_systems_admin: 5
  data_bi_ai: 5
  product_project_ops: 5
  digital_marketing_growth: 5
  total: 20

seat_mix:
  early: { seats: 6, price: 649 }
  standard: { seats: 10, price: 699 }
  installment: { seats: 4, price: 720 }
  blended_average: 688.20

timing:
  delivery_weeks: 12
  m365_access_before_launch: 1
  extension_wrapup: 1
  m365_billing_months: 4

financial:
  vat_applies: true
  vat_rate: 0.19
  payment_processing_fee: 0.025
  external_cost_contingency: 0.15
  target_cash_surplus_margin: 0.05

launch_gates:
  minimum_total_participants: 16
  minimum_per_workstream: 4
  minimum_secured_net_revenue: 10000
  secured_net_revenue_to_date: 0
  workload_multiplier: 1.0
  workload_review_threshold: 24

mentors:
  contact_hours_per_week: 2
  prep_hours_per_week: 2
  setup_hours: 8
  hourly_rate: 20
  capacity_per_mentor: 6

internal_team:
  solomon: { hours: 4.5, weeks: 12, rate: 20, payment: 1080, m365: true }
  david: { hours: 3.5, weeks: 12, rate: 20, payment: 840, m365: true }
  akua: { hours: 3.5, weeks: 12, rate: 20, payment: 840, m365: true }
  intern: { hours: 4.0, weeks: 12, rate: 15, payment: 720, m365: true }
  volunteer_1: { hours: 2.0, weeks: 12, rate: 15, payment: 360, m365: true }
  volunteer_2: { hours: 2.0, weeks: 12, rate: 15, payment: 360, m365: true }
  total: 4200

other_external:
  accounting_vat: { included: true, cost: 350 }
  legal_review: { included: true, cost: 500 }
  insurance: { included: false, cost: 0 }
  recruitment_ads: { included: false, cost: 0 }
  venue_travel: { included: false, cost: 0 }
  total_included: 850

m365:
  price_per_account_per_month: 7.28
  total_accounts: 30
  billing_months: 4
  total_cost: 873.60

tools:
  shared_storage_domain: 100
  it_training_tenant: 150
  it_azure_credits: 100
  it_vm_fallback: 150
  it_jira: 0
  data_cloud_db: 75
  data_power_bi: 0
  data_ai_account: 0
  ops_jira_confluence: 0
  ops_tool_upgrade: 0
  marketing_canva: 0
  marketing_email_crm: 0
  marketing_campaign: 300
  marketing_landing: 0
  total_other_tools: 875

base_case_outputs:
  participant_gross_receipts: 13764.00
  vat_payable: 2197.61
  net_programme_revenue: 11566.39
  mentor_cost: 4480.00
  m365_licences: 873.60
  other_tools: 875.00
  internal_team: 4200.00
  other_external: 850.00
  payment_fees: 344.10
  contingency: 1113.41
  total_cash_cost: 12736.11
  cash_surplus: -1169.72
  cash_surplus_margin: -0.1011
  cash_cost_per_participant: 636.81
  cash_break_even_price: 760.26
  target_margin_price: 801.77
  projected_economics: REVIEW
  launch_readiness: HOLD
```

---

## 11. Potential Extensions (Priority Order)

1. **Scenario comparison side-by-side** — Lock two scenarios and diff them
2. **Historical cohort tracking** — SQLite DB to save/load past cohorts
3. **User authentication** — Founder login with role-based access (Solomon/David/Akua/Intern)
4. **PDF export** — Generate investor-ready one-pager from any panel
5. **Currency toggle** — EUR/USD/GBP with live conversion rates
6. **Tax/VAT modeling** — Add German trade tax, solidarity surcharge
7. **Team lead cost breakdown by role** — Per-mentor cost cards
8. **Alerts** — Toast notifications when margin drops below threshold
9. **Docker deployment** — `docker-compose.yml` for one-command launch
10. **Unit tests** — pytest for backend, Vitest for frontend

---

## 12. Development Commands

```bash
# Backend
cd clp_cost_model
python3 -m venv backend/.venv
source backend/.venv/bin/activate
pip install -r backend/requirements.txt
uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000

# Frontend
cd clp_cost_model/frontend
npm install
npm run dev
# Open http://localhost:5173
```

---

## 13. Notes for AI Assistance

- **Python 3.9 compatibility:** No `X | Y` union syntax. Use `Optional[X]` from `typing`.
- **Pydantic v1:** Use `BaseModel` with `Field(default=...)`. Avoid v2 syntax.
- **React 18:** Functional components + hooks only. No class components.
- **Recharts:** Use `ResponsiveContainer` for all charts. Handle empty data gracefully.
- **Excel parity:** Every number in the dashboard must match the Excel v4.0 base case to 2 decimal places. Use the defaults above as test fixtures.
- **File paths:** All backend modules live in `backend/`. All frontend components live in `frontend/src/components/`.
- **The original `cost_model.py`** at project root is standalone and should not be modified. The new engine lives in `backend/engine.py`.
