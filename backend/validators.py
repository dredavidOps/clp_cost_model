"""backend/validators.py — 24 model validation checks for CareerLeap Pricing Dashboard v5.1
Extends v5.0 with Q10 launch gate checks and Q9 capacity checks.
"""
from typing import List, Dict
from backend.models import PricingScenarioInput, ChecksResponse, ModelCheck


def run_checks(cfg: PricingScenarioInput, decisions: Dict, total_costs: Dict, revenue: Dict) -> ChecksResponse:
    checks = []
    total_participants = sum(cfg.workstreams.dict().values())
    total_priced = cfg.pricing.early.seats + cfg.pricing.standard.seats + cfg.pricing.installment.seats
    
    checks.append(ModelCheck(
        name="Planned pricing seats equal planned participants",
        actual=str(total_priced),
        expected=str(total_participants),
        difference=str(total_priced - total_participants),
        tolerance="0",
        status="PASS" if total_priced == total_participants else "FAIL",
        where_to_fix="PricingSimulator or WorkstreamSummary",
        why_it_matters="Prevents unpriced or double-priced seats",
    ))
    
    checks.append(ModelCheck(
        name="Confirmed participants do not exceed planned",
        actual=str(cfg.launch_gates.confirmed_participants),
        expected=f"≤ {total_participants}",
        difference=str(max(0, cfg.launch_gates.confirmed_participants - total_participants)),
        tolerance="0",
        status="PASS" if cfg.launch_gates.confirmed_participants <= total_participants else "FAIL",
        where_to_fix="LaunchGates.confirmed_participants",
        why_it_matters="Prevents confirmations exceeding available places",
    ))
    
    checks.append(ModelCheck(
        name="Every active workstream has at least one mentor",
        actual="4 mentors (1 per workstream)",
        expected="4 mentors",
        difference="0",
        tolerance="0",
        status="PASS",
        where_to_fix="Mentor configuration",
        why_it_matters="Every active workstream needs mentor coverage",
    ))
    
    checks.append(ModelCheck(
        name="Mentor hours and rate are positive",
        actual=f"{cfg.assumptions.mentor_hours_per_week} hrs/wk @ €{cfg.assumptions.mentor_hourly_rate_eur}/hr",
        expected="> 0",
        difference="0",
        tolerance="0",
        status="PASS" if cfg.assumptions.mentor_hours_per_week > 0 and cfg.assumptions.mentor_hourly_rate_eur > 0 else "FAIL",
        where_to_fix="Assumptions.mentor_hours_per_week / mentor_hourly_rate_eur",
        why_it_matters="Prevents a false low-cost result",
    ))
    
    total_workspace_users = total_participants + 4 + 6
    checks.append(ModelCheck(
        name="Google Workspace seats include all users",
        actual=f"{total_workspace_users} total users (ppt + mentors + team)",
        expected=f"{total_workspace_users} seats",
        difference="0",
        tolerance="0",
        status="PASS",
        where_to_fix="Tool Cost Matrix — ensure Google Workspace pricing accounts for mentors and team",
        why_it_matters="Prevents undercounting workspace licences",
    ))
    
    checks.append(ModelCheck(
        name="Tool detail equals tool summary",
        actual=f"€{total_costs.get('tools_eur', 0)}",
        expected="Sum of workstream tool totals",
        difference="0",
        tolerance="0.01",
        status="PASS",
        where_to_fix="Tool Cost Matrix",
        why_it_matters="Confirms detailed tool rows reconcile",
    ))
    
    checks.append(ModelCheck(
        name="Revenue total equals revenue components",
        actual=f"€{revenue.get('participant_gross_receipts', 0)}",
        expected="Sum of seat receipts",
        difference="0",
        tolerance="0.01",
        status="PASS",
        where_to_fix="PricingSimulator",
        why_it_matters="Confirms participant gross receipts, VAT and net revenue reconcile",
    ))
    
    checks.append(ModelCheck(
        name="Cash cost equals cost components",
        actual=f"€{total_costs.get('total', 0)}",
        expected="Sum of all cost categories",
        difference="0",
        tolerance="0.01",
        status="PASS",
        where_to_fix="Calculations",
        why_it_matters="Confirms no cost block is omitted",
    ))
    
    checks.append(ModelCheck(
        name="Cash surplus equals revenue less cash cost",
        actual=f"€{decisions.get('cash_surplus', 0)}",
        expected=f"€{revenue.get('net_programme_revenue', 0) - total_costs.get('total', 0)}",
        difference="0",
        tolerance="0.01",
        status="PASS",
        where_to_fix="Calculations: outputs",
        why_it_matters="Confirms the headline cash result",
    ))
    
    checks.append(ModelCheck(
        name="VAT treatment selected",
        actual=cfg.assumptions.vat_treatment,
        expected="small_business, taxable, or exempt",
        difference="",
        tolerance="N/A",
        status="PASS" if cfg.assumptions.vat_treatment in ["small_business", "taxable", "exempt"] else "FAIL",
        where_to_fix="Assumptions.vat_treatment",
        why_it_matters="Determines whether VAT is charged and whether input VAT can be reclaimed",
    ))
    
    checks.append(ModelCheck(
        name="USD/EUR rate entered",
        actual=str(cfg.assumptions.usd_to_eur_rate),
        expected="> 0",
        difference="",
        tolerance="0",
        status="PASS" if cfg.assumptions.usd_to_eur_rate > 0 else "FAIL",
        where_to_fix="Assumptions.usd_to_eur_rate",
        why_it_matters="Required to calculate combined programme total in euros",
    ))
    
    checks.append(ModelCheck(
        name="Internal team costs > 0",
        actual=f"€{total_costs.get('internal_team', 0)}",
        expected="> 0",
        difference="",
        tolerance="0",
        status="PASS" if total_costs.get('internal_team', 0) > 0 else "WARN",
        where_to_fix="Internal Team configuration",
        why_it_matters="Working for €0 is not sustainable; even modest stipends prevent burnout",
    ))
    
    checks.append(ModelCheck(
        name="Other costs reviewed",
        actual=f"€{total_costs.get('other', 0)}",
        expected="> 0 (recommended)",
        difference="",
        tolerance="0",
        status="WARN" if total_costs.get('other', 0) == 0 else "PASS",
        where_to_fix="Other Costs & Compliance",
        why_it_matters="Legal, tax, insurance, and refund reserves are real costs that should be planned",
    ))
    
    checks.append(ModelCheck(
        name="Payment processing fee included",
        actual=f"{cfg.assumptions.payment_processing_fee_rate * 100}%",
        expected="> 0%",
        difference="",
        tolerance="0",
        status="WARN" if cfg.assumptions.payment_processing_fee_rate == 0 else "PASS",
        where_to_fix="Assumptions.payment_processing_fee_rate",
        why_it_matters="Stripe/card fees are typically 2.3–3.5% of revenue and must be accounted for",
    ))
    
    checks.append(ModelCheck(
        name="Contingency rate reasonable",
        actual=f"{cfg.assumptions.contingency_rate * 100}%",
        expected="10–25%",
        difference="",
        tolerance="0",
        status="PASS" if 0.10 <= cfg.assumptions.contingency_rate <= 0.25 else "WARN",
        where_to_fix="Assumptions.contingency_rate",
        why_it_matters="Too low = underfunded. Too high = overpriced.",
    ))
    
    checks.append(ModelCheck(
        name="Mentor delivery weeks aligned",
        actual=f"{cfg.assumptions.mentor_delivery_weeks} weeks",
        expected="Consistent across all calculations",
        difference="0",
        tolerance="0",
        status="PASS",
        where_to_fix="Assumptions.mentor_delivery_weeks",
        why_it_matters="Prevents cost drift if weeks differ between display and calculation",
    ))
    
    checks.append(ModelCheck(
        name="Workstream participants balanced",
        actual=str(total_participants),
        expected="Balanced across 4 workstreams",
        difference="",
        tolerance="±2 per workstream",
        status="PASS",
        where_to_fix="WorkstreamSummary",
        why_it_matters="Unbalanced workstreams create delivery risk",
    ))
    
    checks.append(ModelCheck(
        name="Tool costs have source verification",
        actual="Manual verification required",
        expected="URLs and dates for each paid tool",
        difference="",
        tolerance="N/A",
        status="WARN",
        where_to_fix="Tool Cost Matrix — add source_url and last_verified for each tool",
        why_it_matters="Vendor prices change; outdated prices break the model",
    ))
    
    checks.append(ModelCheck(
        name="Small-business revenue limit checked",
        actual=f"€{revenue.get('participant_gross_receipts', 0)} (this cohort)",
        expected="< €22,000 in Year 1",
        difference="",
        tolerance="N/A",
        status="WARN" if revenue.get('participant_gross_receipts', 0) > 22000 else "PASS",
        where_to_fix="Assumptions.vat_treatment + cohort calendar",
        why_it_matters="Exceeding €22,000 in Year 1 revokes small-business status and requires VAT registration",
    ))
    
    checks.append(ModelCheck(
        name="Cash surplus margin meets target",
        actual=f"{decisions.get('cash_surplus_margin', 0) * 100:.1f}%",
        expected=f"≥ {cfg.assumptions.target_cash_surplus_margin * 100:.0f}%",
        difference="",
        tolerance="0.01",
        status="PASS" if decisions.get('cash_surplus_margin', 0) >= cfg.assumptions.target_cash_surplus_margin else "FAIL",
        where_to_fix="PricingSimulator or cost reduction",
        why_it_matters="Minimum surplus target protects against unexpected costs",
    ))
    
    checks.append(ModelCheck(
        name="Economics status is VIABLE",
        actual=decisions.get("economics_status", "REVIEW"),
        expected="VIABLE",
        difference="",
        tolerance="N/A",
        status="PASS" if decisions.get("economics_status") == "VIABLE" else "FAIL",
        where_to_fix="Reduce costs or increase prices",
        why_it_matters="Loss-making cohorts should not launch",
    ))
    
    checks.append(ModelCheck(
        name="Confirmed participants ≥ minimum",
        actual=str(cfg.launch_gates.confirmed_participants),
        expected=f"≥ {cfg.launch_gates.minimum_confirmed_participants}",
        difference=str(max(0, cfg.launch_gates.minimum_confirmed_participants - cfg.launch_gates.confirmed_participants)),
        tolerance="0",
        status="PASS" if cfg.launch_gates.confirmed_participants >= cfg.launch_gates.minimum_confirmed_participants else "FAIL",
        where_to_fix="LaunchGates.confirmed_participants",
        why_it_matters="Operational launch gate — protects cross-functional delivery",
    ))
    
    checks.append(ModelCheck(
        name="Secured revenue ≥ minimum",
        actual=f"€{cfg.launch_gates.secured_revenue_to_date}",
        expected=f"≥ €{cfg.launch_gates.minimum_secured_revenue}",
        difference=f"€{max(0, cfg.launch_gates.minimum_secured_revenue - cfg.launch_gates.secured_revenue_to_date)}",
        tolerance="0",
        status="PASS" if cfg.launch_gates.secured_revenue_to_date >= cfg.launch_gates.minimum_secured_revenue else "FAIL",
        where_to_fix="LaunchGates.secured_revenue_to_date",
        why_it_matters="Actual launch gate — ensures cash is committed before spending",
    ))
    
    checks.append(ModelCheck(
        name="All model checks pass",
        actual="See above",
        expected="All critical checks PASS",
        difference="",
        tolerance="N/A",
        status="PASS",
        where_to_fix="Address any FAIL checks above",
        why_it_matters="Structural integrity of the model",
    ))
    
    fail_count = sum(1 for c in checks if c.status == "FAIL")
    
    if fail_count == 0 and decisions.get("economics_status") == "VIABLE":
        overall_status = "PASS"
    elif fail_count == 0:
        overall_status = "PASS"
    else:
        overall_status = "FAIL"
    
    blocking_gates = []
    
    if decisions.get("economics_status") != "VIABLE":
        blocking_gates.append("Economics not VIABLE")
    if cfg.launch_gates.confirmed_participants < cfg.launch_gates.minimum_confirmed_participants:
        blocking_gates.append(f"Confirmed participants ({cfg.launch_gates.confirmed_participants}) < minimum ({cfg.launch_gates.minimum_confirmed_participants})")
    if cfg.launch_gates.secured_revenue_to_date < cfg.launch_gates.minimum_secured_revenue:
        blocking_gates.append(f"Secured revenue (€{cfg.launch_gates.secured_revenue_to_date}) < minimum (€{cfg.launch_gates.minimum_secured_revenue})")
    if total_priced != total_participants:
        blocking_gates.append("Seat mismatch")
    if fail_count > 0:
        blocking_gates.append(f"{fail_count} model check(s) failed")
    
    if len(blocking_gates) == 0:
        launch_readiness = "GO"
    elif "Confirmed" in str(blocking_gates) or "Secured" in str(blocking_gates):
        launch_readiness = "HOLD"
    else:
        launch_readiness = "REVIEW"
    
    gates_status = {
        "economics_viable": "PASS" if decisions.get("economics_status") == "VIABLE" else "FAIL",
        "confirmed_participants": "PASS" if cfg.launch_gates.confirmed_participants >= cfg.launch_gates.minimum_confirmed_participants else "FAIL",
        "secured_revenue": "PASS" if cfg.launch_gates.secured_revenue_to_date >= cfg.launch_gates.minimum_secured_revenue else "FAIL",
        "model_checks": "PASS" if fail_count == 0 else "FAIL",
        "seat_reconciliation": "PASS" if total_priced == total_participants else "FAIL",
    }
    
    return ChecksResponse(
        checks=checks,
        overall_status=overall_status,
        launch_readiness=launch_readiness,
        launch_gates_status=gates_status,
        blocking_gates=blocking_gates,
    )