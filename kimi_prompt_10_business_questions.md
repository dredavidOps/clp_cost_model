# Kimi Code Prompt: Implement 10 Business Decision Questions
## CareerLeap Pricing Dashboard — Feature Enhancement

**Date:** 2026-09-06
**Context:** The CareerLeap Pricing Dashboard (v5) is a FastAPI + React app that replicates an Excel pricing model. The current implementation has basic calculation, summary cards, cost breakdown, break-even curves, sensitivity heatmaps, and model checks. This prompt adds 10 business-critical decision features.

**Reference files:**
- `CareerLeap_Unified_Spec_v5.md` — authoritative product spec
- `backend/models.py` — Pydantic v1 schemas
- `backend/engine.py` — calculation engine
- `backend/validators.py` — 21 model checks
- `frontend/src/store.js` — Zustand state
- `frontend/src/components/` — existing dashboard panels

---

## INSTRUCTION

Implement the 10 business questions below as new or enhanced dashboard features. For each question, I specify:
- **What already exists** (do not break it)
- **What needs to be built** (new fields, new endpoints, new UI components)
- **Exact formulas** (so the numbers match Excel logic)
- **UI placement** (which component or new component)

Keep Python 3.9 compatibility. Use Pydantic v1. Round currencies to 2 decimals via `_r()`. Update both backend AND frontend for each feature.

---

## QUESTION 1: What is the complete cost of running one cohort?

**Current state:** `CostBreakdownChart.jsx` shows a pie chart of tools, mentors, internal team, operational, other costs. `SummaryCards.jsx` shows "Total Programme Cost".

**What to add:**
- A **"Complete Cost Statement"** table in a new component `CompleteCostStatement.jsx`
- Show every line item that makes up the total, with subtotals and the grand total
- Include both EUR and USD columns for tool costs

**Backend:**
- Extend `TotalCostResult` in `models.py` to include a `line_items` array:
  ```python
  class CostLineItem(BaseModel):
      category: str  # "Tools", "Mentors", "Internal Team", "Operational", "Other"
      subcategory: Optional[str]  # e.g. "Google Workspace", "Solomon stipend"
      amount_eur: float
      amount_usd: Optional[float]  # for tool items only
      basis: str  # human-readable calculation basis
  ```
- In `engine.py`, `calculate_total_cost()` should populate this array before rounding

**Frontend:**
- New component `CompleteCostStatement.jsx` — a detailed table with expandable categories
- Place it below `CostBreakdownChart.jsx` in the layout
- Show: Category | Subcategory | Basis | Amount (EUR) | Amount (USD)
- Grand total row bold, highlighted

**Fixture test:** At defaults, total = €21,622.25 (or corrected €21,918.95 if Google Workspace seats fixed)

---

## QUESTION 2: What is the actual cost per participant?

**Current state:** `SummaryCards.jsx` shows "Cost Per Participant" as a single number.

**What to add:**
- Break cost-per-participant down by **category** (tools/ppt, mentors/ppt, team/ppt, ops/ppt, other/ppt)
- Show a **"Cost Per Participant Waterfall"** — stacked bar or table showing how each category contributes to the total €540.56 (or corrected)
- Add a **"Cost Per Participant by Workstream"** view — since each workstream has different tool costs

**Backend:**
- Extend `TotalCostResult`:
  ```python
  class TotalCostResult(BaseModel):
      # ... existing fields ...
      per_participant_breakdown: Dict[str, float]  # {"tools": 137.22, "mentors": 120.00, ...}
      per_participant_by_workstream: Dict[str, float]  # {"itsa": 229.25, "data": 275.25, ...}
  ```
- In `engine.py`, after calculating totals, divide each category by `total_participants`
- Per-workstream cost = (workstream tools + mentor share + team share + ops share + other share) / participants
  - Mentor share per workstream = mentor cost / total participants
  - Team/ops/other are shared equally across all participants

**Frontend:**
- New component `CostPerParticipantDetail.jsx`
- Two tabs: (1) Category Breakdown, (2) By Workstream
- Category tab: horizontal stacked bar showing €137 tools + €120 mentors + €270 team + €14 ops = €540 total
- Workstream tab: 4 bars (ITSA, Data, Marketing, Product) showing different per-ppt costs

**Fixture test:**
- Tools/ppt = €137.22, Mentors/ppt = €120.00, Team/ppt = €269.51, Ops/ppt = €13.83
- ITSA/ppt = €229.25 (tools €109.25 + shared €120), Data/ppt = €275.25, Marketing/ppt = €384.50, Product/ppt = €229.25

---

## QUESTION 3: What minimum participant price is required to break even?

**Current state:** `BreakEvenChart.jsx` shows a curve. The break-even price is calculated but not prominently displayed.

**What to add:**
- A **big, live-updating number** in `SummaryCards.jsx`: "Break-Even Price: €XXX"
- Color coding: GREEN if current average price > break-even, RED if below
- A **"Distance to Break-Even"** indicator: "Your average price (€688) is €72 BELOW break-even"
- The break-even price should be calculated at the **current cohort size**, not just the curve

**Backend:**
- Already exists in `engine.py` as `cash_break_even_average_price`
- Ensure it is returned in `CalculateResponse` → `DecisionsResult`
- Formula (from Excel): solve for price where `cash_surplus = 0` at current `total_participants`
  ```python
  # Break-even price = total_costs / total_participants / (1 - payment_fee_rate)
  # If VAT applies: divide by (1 + vat_rate) first
  break_even_price = total_costs / total_participants / (1 - payment_processing_fee_rate)
  if vat_applies:
      break_even_price = break_even_price / (1 + vat_rate)
  ```

**Frontend:**
- In `SummaryCards.jsx`, add a new card: "Break-Even Price"
  - Large font: €573.00 (at 40 ppt, default costs)
  - Subtitle: "Minimum average price to cover all costs"
  - Color: green if `average_gross_price >= break_even_price`, else red
- Add a card: "Distance to Break-Even"
  - "Your price €688 is €115 above break-even ✅" (green)
  - OR "Your price €500 is €73 below break-even ⚠️" (red)

**Fixture test:** At defaults (40 ppt, €21,622 cost), break-even = €21,622 / 40 / 0.977 = **€553.27**

---

## QUESTION 4: What price should we charge to achieve our target profit margin?

**Current state:** `engine.py` calculates `target_margin_average_price`. It may be in the response but is not prominently shown.

**What to add:**
- A **"Target Margin Price"** card in `SummaryCards.jsx`
- A **slider** in `PricingSimulator.jsx`: "Target margin %" — default 5%, range 0–50%
- Live update: as user drags the slider, the target price and required participant count update
- Show the **price gap**: "Raise price by €113 to hit 5% margin" or "You already exceed 5% margin by €87"

**Backend:**
- Already exists: `target_margin_average_price` in `DecisionsResult`
- Ensure it accepts a dynamic target margin (currently hardcoded to 5%)
- Add to `PricingScenarioInput.assumptions`: `target_cash_surplus_margin: float = 0.05` (already exists, verify)
- Formula:
  ```python
  # target_revenue = total_costs / (1 - target_margin)
  # target_gross_receipts = target_revenue / (1 - payment_fee_rate)
  # target_price = target_gross_receipts / total_participants
  # if VAT applies: target_price = target_price / (1 + vat_rate)
  ```

**Frontend:**
- In `SummaryCards.jsx`: "Target Margin Price (5%)" = €801.77 (at defaults)
- In `PricingSimulator.jsx`: add a slider input for target margin %
- Show: "At 10% margin, charge €890 | At 20% margin, charge €1,025"
- Show a **recommendation badge**: "Recommended: €875" (if target margin is achievable)

**Fixture test:** At defaults, target margin price (5%) = **€801.77**

---

## QUESTION 5: How many paying participants are required to break even?

**Current state:** NOT calculated. The model shows break-even price, not break-even cohort size.

**What to add:**
- A **"Break-Even Cohort Size"** number in `SummaryCards.jsx`
- At the **current average price**, how many participants are needed to cover all costs?
- A **"Minimum Viable Cohort"** warning: "You need at least 25 participants at €850 to break even"
- In `SensitivityHeatmap.jsx`, highlight the break-even cell (where surplus = 0)

**Backend:**
- New field in `DecisionsResult`:
  ```python
  break_even_cohort_size: float  # participants needed at current average price
  minimum_viable_cohort_size: int  # ceil(break_even_cohort_size)
  ```
- Formula:
  ```python
  # At current average price, how many participants to cover costs?
  # revenue_per_ppt = average_gross_price * (1 - payment_fee_rate) * (1 - vat_rate if applicable)
  # break_even_size = total_costs / revenue_per_ppt
  revenue_per_ppt = average_gross_price * (1 - payment_processing_fee_rate)
  if vat_applies:
      revenue_per_ppt = revenue_per_ppt / (1 + vat_rate)
  break_even_size = total_costs / revenue_per_ppt
  ```
- Note: This is the INVERSE of the break-even price calculation

**Frontend:**
- In `SummaryCards.jsx`: new card "Break-Even Participants"
  - "At €850 average price, you need 26 participants to break even"
  - "Current plan: 40 ✅" (green) or "Current plan: 20 ❌" (red)
- In `SensitivityHeatmap.jsx`: draw a contour line or highlight cells where surplus = 0
- In `PricingSimulator.jsx`: show "At this price, minimum participants = X"

**Fixture test:** At defaults (€688 average price, €21,622 cost), break-even size = €21,622 / (€688 × 0.977) = **32.2 participants** → 33 needed

---

## QUESTION 6: What revenue, cash surplus, pre-tax profit and margin will the cohort generate?

**Current state:** `SummaryCards.jsx` shows revenue, surplus, margin. "Pre-tax profit" is not explicitly labeled (it is the same as cash surplus in this model).

**What to add:**
- A **"Financial Outcome"** panel that shows all 4 numbers in one place
- Clarify that "pre-tax profit" = "cash surplus" in this model (before business income tax)
- Add a **margin gauge** — visual dial or progress bar showing margin %
- Add a **"Revenue Bridge"** — walk from gross receipts → net revenue → after costs → surplus

**Backend:**
- Already exists in `CalculateResponse`:
  - `revenue.participant_gross_receipts`
  - `revenue.net_programme_revenue`
  - `decisions.cash_surplus`
  - `decisions.cash_surplus_margin`
- Add explicit field: `pre_tax_profit = cash_surplus` (same value, different label for clarity)
- Add `revenue_bridge` array to `RevenueResult`:
  ```python
  class RevenueBridgeItem(BaseModel):
      label: str
      amount: float
      operation: str  # "add", "subtract", "equals"
  ```
  Example: Gross Receipts €13,764 → minus VAT €0 → equals Net Revenue €13,764 → minus Costs €21,622 → equals Cash Surplus -€7,858

**Frontend:**
- New component `FinancialOutcomePanel.jsx`
- 4 big numbers in a row: Revenue | Net Revenue | Pre-Tax Profit | Margin %
- Below: a vertical "waterfall" chart (Recharts BarChart with positive/negative bars) showing the revenue bridge
- Color: green for revenue, red for costs, net color for surplus

**Fixture test:** At defaults: Gross €13,764 | Net €13,764 | Surplus -€7,858 | Margin -57.1%

---

## QUESTION 7: How much cash is required before the cohort starts, and when could cash shortages occur?

**Current state:** Cash flow timing exists in the model logic but is not prominently displayed. No "cash required before start" or "shortage warning" feature.

**What to add:**
- A **"Cash Required Before Launch"** number — the minimum cash buffer needed
- A **"Cash Shortage Warning"** — highlight the week/month where cash balance is lowest
- A **"Pre-Launch Funding Need"** card — how much cash must be in the bank before cohort starts
- Enhanced `CashFlowPanel.jsx` with a line chart showing opening/closing balance over time

**Backend:**
- Extend `CalculateResponse` with new `cash_flow` section:
  ```python
  class CashFlowResult(BaseModel):
      pre_launch_funding_required: float  # absolute value of lowest negative balance
      lowest_balance_week: str  # e.g. "Week 6"
      lowest_balance_amount: float
      ending_balance: float
      monthly_schedule: List[CashFlowMonth]
  ```
- Formula for pre-launch funding:
  ```python
  # Simulate cash flow week by week
  # opening_balance = 0
  # For each phase (pre-launch, month 1, month 2, month 3, extension):
  #   cash_in = net_revenue × revenue_collection_profile[phase]
  #   cash_out = total_costs × cost_payment_profile[phase]
  #   closing_balance = opening_balance + cash_in - cash_out
  #   opening_balance = closing_balance (for next phase)
  # pre_launch_funding = max(0, -min(closing_balance across all phases))
  ```
- Default timing profiles (from Excel):
  - Revenue: Pre-launch 40%, Month 1 25%, Month 2 20%, Month 3 10%, Extension 5%
  - Costs: Pre-launch 25%, Month 1 25%, Month 2 20%, Month 3 20%, Extension 10%

**Frontend:**
- New component `CashFlowPanel.jsx` (or enhance existing if partial)
- Line chart: X-axis = phase, Y-axis = cash balance, line = closing balance
- Horizontal reference line at €0
- Highlight the lowest point with a red dot and label
- Card: "Pre-Launch Cash Required: €1,170" (at defaults)
- Card: "Lowest Balance: -€1,170 in Extension phase"
- Warning banner if `pre_launch_funding_required > 0`: "⚠️ You need €X in reserve before launching"

**Fixture test:** At defaults, pre-launch funding required = **€1,170** (from Excel Cash Flow sheet)

---

## QUESTION 8: What happens if participant numbers, prices, programme duration or costs change?

**Current state:** `SensitivityHeatmap.jsx` shows a 2D grid of price vs. cohort size. `BreakEvenChart.jsx` shows price-surplus curve. Users can manually edit inputs.

**What to add:**
- **"Scenario Comparison"** panel — save 3 scenarios and compare side-by-side
- **"What-If Sliders"** — quick sliders for key variables that update the whole dashboard instantly
- **"Impact Analysis"** — "If you change X by Y%, margin changes by Z%"

**Backend:**
- New endpoint `POST /api/scenarios/compare`:
  ```python
  class ScenarioCompareRequest(BaseModel):
      scenarios: List[PricingScenarioInput]  # 2 or 3 scenarios

  class ScenarioCompareResponse(BaseModel):
      comparisons: List[ScenarioComparison]
  ```
- Already exists: `POST /api/calculate/sensitivity` for heatmap data
- Enhance sensitivity to include **duration** and **cost** dimensions (currently only price × size)

**Frontend:**
- New component `ScenarioComparison.jsx`
- Table with 3 columns: Scenario A | Scenario B | Delta
- Rows: participants, price, revenue, costs, surplus, margin, break-even price
- New component `WhatIfSliders.jsx`:
  - Sliders for: participant count, average price, mentor rate, tool cost %, team cost %
  - Each slider updates the store and re-runs calculations
  - Show "Impact on margin" next to each slider
- In `SensitivityHeatmap.jsx`: add dropdown to switch axes:
  - Price vs. Size (existing)
  - Duration vs. Size
  - Mentor rate vs. Size
  - Tool cost vs. Size

**Fixture test:** Compare defaults vs. "+10 participants" vs. "-€100 price" scenarios

---

## QUESTION 9: Can the planned mentors, internal team and software licences support the cohort size?

**Current state:** `ModelChecks.jsx` shows 21 validation checks. `WorkstreamToolsTable.jsx` shows tool costs.

**What to add:**
- **"Capacity Dashboard"** — green/amber/red indicators for mentor capacity, team bandwidth, tool limits
- **Mentor capacity check:** "Each mentor can handle 6 participants. With 4 mentors, max capacity = 24. Current: 40 ❌"
- **Tool limit check:** "Jira Cloud free tier = 10 agents. IT participants = 10 ✅" or "11 ❌"
- **Team bandwidth check:** "Internal team hours = 20 hrs/wk. At 40 participants, recommended = 30 hrs/wk ⚠️"

**Backend:**
- New endpoint `POST /api/calculate/capacity`:
  ```python
  class CapacityResult(BaseModel):
      mentor_capacity_status: str  # "OK", "WARNING", "FAIL"
      mentor_capacity_detail: str  # "4 mentors × 6 capacity = 24 max. Current: 40 participants"
      tool_limit_status: str
      tool_limit_details: List[dict]  # [{"tool": "Jira", "limit": 10, "current": 10, "status": "OK"}]
      team_bandwidth_status: str
      team_bandwidth_detail: str
  ```
- Mentor capacity formula:
  ```python
  mentor_capacity = num_mentors * mentor_capacity_per_mentor  # default 6 per mentor
  if total_participants <= mentor_capacity: status = "OK"
  elif total_participants <= mentor_capacity * 1.25: status = "WARNING"
  else: status = "FAIL"
  ```
- Tool limit checks (from tool matrix):
  ```python
  # Jira Cloud free: 10 agents
  # Jira Work Management free: 10 users
  # Google Workspace: no hard limit (paid per seat)
  # Slack free: 10,000 message history
  # Notion free: unlimited pages
  # Check each tool with a free_tier_limit and compare to actual users
  ```

**Frontend:**
- New component `CapacityDashboard.jsx`
- 3 big cards: Mentors | Tools | Team
- Each card: capacity bar (current / max), status color, detail text
- Red card = launch blocker, amber = risk, green = good
- Place above `ModelChecks.jsx` in the layout

**Fixture test:** At defaults (40 ppt, 4 mentors, 6 capacity each): mentor status = "FAIL" (40 > 24)

---

## QUESTION 10: Based on confirmed participants and secured revenue, should the cohort launch: GO, HOLD or REVIEW?

**Current state:** `validators.py` returns `launch_readiness` as "GO" or "HOLD". It checks if economics are VIABLE and priced seats == participants. It does NOT check confirmed participants or secured revenue.

**What to add:**
- **"Launch Control Panel"** — a dedicated component with all launch gates
- Input fields for: `confirmed_participants` and `secured_revenue_to_date`
- Gates:
  1. Economics VIABLE? (margin >= target)
  2. Confirmed participants >= minimum? (default 16)
  3. Secured revenue >= minimum? (default €10,000)
  4. Model checks PASS?
  5. Priced seats == planned participants?
- Status: **GO** (all green), **HOLD** (any red), **REVIEW** (any amber)
- Show which specific gate is blocking launch

**Backend:**
- Add to `PricingScenarioInput`:
  ```python
  class LaunchGates(BaseModel):
      confirmed_participants: int = 0
      minimum_confirmed_participants: int = 16
      secured_revenue_to_date: float = 0.0
      minimum_secured_revenue: float = 10000.0
  ```
- Update `validators.py` check #21 (or add new checks):
  ```python
  # Check: Confirmed participants >= minimum
  # Check: Secured revenue >= minimum
  # Check: All model checks PASS
  # Check: Economics status == VIABLE
  ```
- Update `DecisionsResult.launch_readiness` logic:
  ```python
  if all_checks_pass and economics == "VIABLE" and confirmed >= min and secured >= min:
      launch_readiness = "GO"
  elif confirmed < min or secured < min:
      launch_readiness = "HOLD"
  else:
      launch_readiness = "REVIEW"
  ```

**Frontend:**
- New component `LaunchControlPanel.jsx`
- Place at the TOP of the dashboard, above all other panels
- 5 gate indicators in a row, each with icon + label + status
- Big banner at top: "LAUNCH STATUS: GO 🟢" or "LAUNCH STATUS: HOLD 🔴"
- If HOLD: list the specific blocking gates: "❌ Only 12/16 participants confirmed" + "❌ Only €0/€10,000 revenue secured"
- Input fields for confirmed participants and secured revenue (editable, stored in config)

**Fixture test:**
- Defaults (confirmed=0, secured=0): status = "HOLD" (blocked by confirmed + secured)
- Confirmed=20, secured=€12,000, economics=VIABLE: status = "GO"
- Confirmed=20, secured=€12,000, economics=REVIEW: status = "REVIEW"

---

## IMPLEMENTATION ORDER (Priority)

| Priority | Question | Files to touch | Est. time |
|----------|----------|---------------|-----------|
| **P0** | Q10: Launch Control Panel | `models.py`, `validators.py`, `LaunchControlPanel.jsx`, `App.jsx` | 2 hrs |
| **P0** | Q3: Break-even price (prominent) | `SummaryCards.jsx` | 30 min |
| **P0** | Q5: Break-even cohort size | `engine.py`, `models.py`, `SummaryCards.jsx` | 1 hr |
| **P1** | Q1: Complete cost statement | `engine.py`, `models.py`, `CompleteCostStatement.jsx` | 2 hrs |
| **P1** | Q2: Cost per participant detail | `engine.py`, `models.py`, `CostPerParticipantDetail.jsx` | 2 hrs |
| **P1** | Q7: Cash required / shortage | `engine.py`, `models.py`, `CashFlowPanel.jsx` | 2 hrs |
| **P1** | Q9: Capacity dashboard | `engine.py`, `models.py`, `CapacityDashboard.jsx` | 2 hrs |
| **P2** | Q4: Target margin price (slider) | `PricingSimulator.jsx`, `SummaryCards.jsx` | 1 hr |
| **P2** | Q6: Financial outcome panel | `FinancialOutcomePanel.jsx` | 1.5 hrs |
| **P2** | Q8: Scenario comparison | `engine.py`, `models.py`, `ScenarioComparison.jsx`, `WhatIfSliders.jsx` | 3 hrs |

---

## TESTING REQUIREMENTS

After implementing each question, verify against these fixture values (at default config):

| Metric | Expected Value |
|--------|---------------|
| Total cost | €21,622.25 |
| Cost per participant | €540.56 |
| Break-even price | €553.27 |
| Break-even cohort size (at €688 avg price) | 32.2 → 33 |
| Target margin price (5%) | €801.77 |
| Cash surplus | -€7,858.25 |
| Cash surplus margin | -57.1% |
| Pre-launch funding required | €1,170 |
| Mentor capacity max | 24 (4 mentors × 6) |
| Launch status (defaults) | HOLD |

Run `pytest` smoke test: POST defaults to `/api/calculate` and assert all fixture values within €0.01.

---

## NOTES

- Do NOT break existing API contracts. Add new fields as optional with defaults.
- Keep Python 3.9 compatibility (no `X | Y`).
- Round all currencies via `_r()` in `engine.py`.
- Update `frontend/src/config.js` if new default fields are added.
- The `AGENTS.md` file should be updated with a note about the new features after implementation.
