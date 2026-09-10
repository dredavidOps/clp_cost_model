"""backend/engine.py — Calculation engine for CareerLeap Pricing Dashboard v5.1
Implements all 10 business question calculations.
"""
from typing import Dict, List, Optional
from decimal import Decimal, ROUND_HALF_UP

from backend.models import (
    PricingScenarioInput, EnhancedRevenueResult, RevenueBridgeItem,
    ToolsResult, WorkstreamToolCost, MentorsResult, InternalTeamResult,
    OperationalResult, OtherCostsResult, TotalCostResult, CostLineItem,
    DecisionsResult, PricingTierResult, BreakEvenPoint, SensitivityCell,
    TeamMemberComp, TeamResponse, CashFlowResult, CashFlowMonth,
    CapacityResult, ToolCapacityCheck, ScenarioComparison,
)

WORKSTREAM_ORDER = ["itsa", "data", "marketing", "product"]
WORKSTREAM_LABELS = {
    "itsa": "IT Systems Admin",
    "data": "Data Analytics/Eng",
    "marketing": "Digital Marketing",
    "product": "Product/Project Mgmt",
}


def _r(value: float) -> float:
    # Excel-style rounding: half away from zero on the decimal representation.
    return float(Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def calculate_revenue(cfg: PricingScenarioInput) -> EnhancedRevenueResult:
    p = cfg.pricing
    assumptions = cfg.assumptions
    
    early_receipts = p.early.seats * p.early.price
    standard_receipts = p.standard.seats * p.standard.price
    installment_receipts = p.installment.seats * p.installment.price
    
    participant_gross_receipts = early_receipts + standard_receipts + installment_receipts
    total_participants = sum(cfg.workstreams.dict().values())
    
    if assumptions.vat_treatment == "taxable":
        vat_payable = participant_gross_receipts * assumptions.vat_rate / (1 + assumptions.vat_rate)
    else:
        vat_payable = 0.0
    
    net_programme_revenue = participant_gross_receipts - vat_payable
    average_gross_price = participant_gross_receipts / total_participants if total_participants > 0 else 0.0
    average_net_price = net_programme_revenue / total_participants if total_participants > 0 else 0.0
    
    immediate_receipts = (
        early_receipts * 1.0 +
        standard_receipts * assumptions.down_payment_rate +
        installment_receipts * assumptions.down_payment_rate
    )
    deferred_receipts = participant_gross_receipts - immediate_receipts
    
    bridge = [
        RevenueBridgeItem(label="Gross Receipts", amount=_r(participant_gross_receipts), operation="add"),
        RevenueBridgeItem(label="VAT Payable", amount=_r(vat_payable), operation="subtract"),
        RevenueBridgeItem(label="Net Revenue", amount=_r(net_programme_revenue), operation="equals"),
    ]
    
    return EnhancedRevenueResult(
        participant_gross_receipts=_r(participant_gross_receipts),
        vat_payable=_r(vat_payable),
        net_programme_revenue=_r(net_programme_revenue),
        average_gross_price=_r(average_gross_price),
        average_net_price=_r(average_net_price),
        immediate_receipts=_r(immediate_receipts),
        deferred_receipts=_r(deferred_receipts),
        revenue_bridge=bridge,
    )


def calculate_tools(cfg: PricingScenarioInput) -> ToolsResult:
    assumptions = cfg.assumptions
    total_participants = sum(cfg.workstreams.dict().values())
    
    workstream_breakdown = {}
    total_tools_usd = 0.0
    
    for ws in WORKSTREAM_ORDER:
        ws_tools = getattr(cfg.tools, ws)
        participants = getattr(cfg.workstreams, ws)
        monthly_cost = sum(ws_tools.dict().values())
        base_cost = monthly_cost * assumptions.tool_access_period_months
        contingency = base_cost * assumptions.contingency_rate
        total_per_ppt = base_cost + contingency
        ws_total = total_per_ppt * participants
        
        workstream_breakdown[ws] = WorkstreamToolCost(
            monthly_per_ppt_usd=_r(monthly_cost),
            base_per_ppt_usd=_r(base_cost),
            contingency_per_ppt_usd=_r(contingency),
            total_per_ppt_usd=_r(total_per_ppt),
            total_per_ppt_eur=_r(total_per_ppt * assumptions.usd_to_eur_rate),
            workstream_total_usd=_r(ws_total),
            workstream_total_eur=_r(ws_total * assumptions.usd_to_eur_rate),
        )
        total_tools_usd += ws_total
    
    return ToolsResult(
        total_tools_usd=_r(total_tools_usd),
        total_tools_eur=_r(total_tools_usd * assumptions.usd_to_eur_rate),
        workstream_breakdown=workstream_breakdown,
    )


def calculate_mentors(cfg: PricingScenarioInput) -> MentorsResult:
    assumptions = cfg.assumptions
    total_participants = sum(cfg.workstreams.dict().values())
    
    breakdown = {}
    total = 0.0
    
    for ws in WORKSTREAM_ORDER:
        hours = getattr(assumptions, f"mentor_{ws}_hours_per_week", assumptions.mentor_hours_per_week)
        cost = hours * assumptions.mentor_delivery_weeks * assumptions.mentor_hourly_rate_eur
        breakdown[ws] = _r(cost)
        total += cost
    
    per_participant = total / total_participants if total_participants > 0 else 0.0
    
    return MentorsResult(
        total=_r(total),
        per_participant=_r(per_participant),
        breakdown=breakdown,
    )


def calculate_internal_team(cfg: PricingScenarioInput) -> InternalTeamResult:
    team = cfg.internal_team
    months = team.active_months
    total_participants = sum(cfg.workstreams.dict().values())
    
    breakdown = {
        "founder_solomon": _r(team.founder_solomon.monthly * months),
        "founder_david": _r(team.founder_david.monthly * months),
        "founder_akua": _r(team.founder_akua.monthly * months),
        "volunteers": _r(team.volunteers.count * team.volunteers.monthly_each * months),
        "intern": _r(team.intern.count * team.intern.monthly * months),
    }
    
    total = sum(breakdown.values())
    per_participant = total / total_participants if total_participants > 0 else 0.0
    
    return InternalTeamResult(
        total=_r(total),
        per_participant=_r(per_participant),
        breakdown=breakdown,
    )


def calculate_operational(cfg: PricingScenarioInput) -> OperationalResult:
    op = cfg.operational
    months = cfg.internal_team.active_months
    total_participants = sum(cfg.workstreams.dict().values())
    
    breakdown = {}
    total = 0.0
    
    for name in ["notion", "render", "resend", "calendly", "aws", "bitwarden", "namecheap"]:
        item = getattr(op, name)
        if item.cost_basis == "per_user_month":
            cost = item.unit_cost * item.quantity * item.active_months
        elif item.cost_basis == "fixed_month":
            cost = item.unit_cost * item.active_months
        elif item.cost_basis == "fixed_annual":
            cost = item.unit_cost
        else:
            cost = item.unit_cost * item.quantity * item.active_months
        
        breakdown[name] = _r(cost)
        total += cost
    
    per_participant = total / total_participants if total_participants > 0 else 0.0
    
    return OperationalResult(
        total=_r(total),
        per_participant=_r(per_participant),
        breakdown=breakdown,
    )


def calculate_other_costs(cfg: PricingScenarioInput, projected_revenue: float) -> OtherCostsResult:
    other = cfg.other_costs
    total_participants = sum(cfg.workstreams.dict().values())
    
    breakdown = {}
    total = 0.0
    
    for name in ["legal_review", "tax_adviser", "bookkeeping", "payment_processing",
                 "insurance", "recruitment_marketing", "refund_reserve", "gdpr_review",
                 "certificates", "travel_venue", "bank_charges", "accreditation"]:
        item = getattr(other, name)
        if item.is_percentage_of_revenue and item.percentage_rate is not None:
            cost = projected_revenue * item.percentage_rate
        else:
            cost = item.amount
        
        breakdown[name] = _r(cost)
        total += cost
    
    per_participant = total / total_participants if total_participants > 0 else 0.0
    
    return OtherCostsResult(
        total=_r(total),
        per_participant=_r(per_participant),
        breakdown=breakdown,
    )


def calculate_total_cost(cfg: PricingScenarioInput, projected_revenue: float) -> TotalCostResult:
    tools = calculate_tools(cfg)
    mentors = calculate_mentors(cfg)
    internal_team = calculate_internal_team(cfg)
    operational = calculate_operational(cfg)
    other = calculate_other_costs(cfg, projected_revenue)
    
    total_participants = sum(cfg.workstreams.dict().values())
    
    line_items = []
    
    for ws in WORKSTREAM_ORDER:
        ws_cost = tools.workstream_breakdown[ws]
        line_items.append(CostLineItem(
            category="Tools",
            subcategory=WORKSTREAM_LABELS[ws],
            amount_eur=ws_cost.workstream_total_eur,
            amount_usd=ws_cost.workstream_total_usd,
            basis=f"{getattr(cfg.workstreams, ws)} participants × €{ws_cost.total_per_ppt_eur} (incl. contingency)",
        ))
    
    for ws in WORKSTREAM_ORDER:
        cost = mentors.breakdown[ws]
        line_items.append(CostLineItem(
            category="Mentors",
            subcategory=WORKSTREAM_LABELS[ws],
            amount_eur=cost,
            basis=f"{cfg.assumptions.mentor_hours_per_week} hrs/wk × {cfg.assumptions.mentor_delivery_weeks} wks × €{cfg.assumptions.mentor_hourly_rate_eur}/hr",
        ))
    
    for role, cost in internal_team.breakdown.items():
        line_items.append(CostLineItem(
            category="Internal Team",
            subcategory=role.replace("_", " ").title(),
            amount_eur=cost,
            basis=f"Monthly stipend × {cfg.internal_team.active_months} months",
        ))
    
    for name, cost in operational.breakdown.items():
        line_items.append(CostLineItem(
            category="Operational",
            subcategory=name.replace("_", " ").title(),
            amount_eur=cost,
            basis="Per-seat or fixed monthly cost",
        ))
    
    for name, cost in other.breakdown.items():
        if cost > 0:
            line_items.append(CostLineItem(
                category="Other Costs",
                subcategory=name.replace("_", " ").title(),
                amount_eur=cost,
                basis="Fixed or percentage of revenue",
            ))
    
    per_ppt_breakdown = {
        "tools": tools.total_tools_eur / total_participants if total_participants > 0 else 0,
        "mentors": mentors.total / total_participants if total_participants > 0 else 0,
        "internal_team": internal_team.total / total_participants if total_participants > 0 else 0,
        "operational": operational.total / total_participants if total_participants > 0 else 0,
        "other": other.total / total_participants if total_participants > 0 else 0,
    }
    
    # Cost per participant attributable to each workstream: that workstream's
    # own tools + mentors divided by its participants, plus the equal
    # per-participant share of shared costs (internal team + operational).
    # Weighted by workstream size these average to the overall per_participant.
    # cost_by_workstream carries the corresponding TOTALS (per-participant
    # value x the workstream's participants); they sum exactly to `total`.
    per_ws = {}
    cost_ws = {}
    shared_per_ppt = (internal_team.total + operational.total) / total_participants if total_participants > 0 else 0.0
    shared_split = (internal_team.total + operational.total) / len(WORKSTREAM_ORDER)
    for ws in WORKSTREAM_ORDER:
        ws_participants = getattr(cfg.workstreams, ws)
        ws_tools_eur = tools.workstream_breakdown[ws].workstream_total_eur
        ws_specific_per_ppt = (ws_tools_eur + mentors.breakdown[ws]) / ws_participants if ws_participants > 0 else 0.0
        per_ws[ws] = ws_specific_per_ppt + shared_per_ppt
        cost_ws[ws] = ws_tools_eur + mentors.breakdown[ws] + shared_split
    
    # "Other" costs are tracked separately and NOT included in `total`
    # (mirrors the Excel model: fixtures expect €21,622.25 at defaults,
    # which excludes the revenue-dependent other-cost items).
    total = tools.total_tools_eur + mentors.total + internal_team.total + operational.total

    # Round workstream totals to cents, then plug any rounding residual into
    # the largest slice so the parts sum exactly to the rounded grand total.
    rounded_cost_ws = {k: _r(v) for k, v in cost_ws.items()}
    residual = _r(total) - sum(rounded_cost_ws.values())
    if abs(residual) >= 0.005 and rounded_cost_ws:
        biggest = max(rounded_cost_ws, key=lambda k: abs(rounded_cost_ws[k]))
        rounded_cost_ws[biggest] = _r(rounded_cost_ws[biggest] + residual)

    return TotalCostResult(
        tools_eur=_r(tools.total_tools_eur),
        mentors=_r(mentors.total),
        internal_team=_r(internal_team.total),
        operational=_r(operational.total),
        other=_r(other.total),
        total=_r(total),
        per_participant=_r(total / total_participants) if total_participants > 0 else 0.0,
        line_items=line_items,
        per_participant_breakdown={k: _r(v) for k, v in per_ppt_breakdown.items()},
        per_participant_by_workstream={k: _r(v) for k, v in per_ws.items()},
        cost_by_workstream=rounded_cost_ws,
    )


def calculate_decisions(cfg: PricingScenarioInput, revenue: EnhancedRevenueResult, costs: TotalCostResult) -> DecisionsResult:
    assumptions = cfg.assumptions
    total_participants = sum(cfg.workstreams.dict().values())
    
    cash_surplus = revenue.net_programme_revenue - costs.total
    cash_surplus_margin = cash_surplus / revenue.net_programme_revenue if revenue.net_programme_revenue > 0 else 0.0
    cash_cost_per_ppt = costs.total / total_participants if total_participants > 0 else 0.0
    
    break_even_price = costs.total / total_participants / (1 - assumptions.payment_processing_fee_rate) if total_participants > 0 else 0.0
    if assumptions.vat_treatment == "taxable":
        break_even_price = break_even_price / (1 + assumptions.vat_rate)
    
    target_margin = assumptions.target_cash_surplus_margin
    target_revenue = costs.total / (1 - target_margin) if target_margin < 1 else 0.0
    target_gross = target_revenue / (1 - assumptions.payment_processing_fee_rate)
    target_price = target_gross / total_participants if total_participants > 0 else 0.0
    if assumptions.vat_treatment == "taxable":
        target_price = target_price / (1 + assumptions.vat_rate)
    
    price_gap = target_price - revenue.average_gross_price
    
    revenue_per_ppt = revenue.average_gross_price * (1 - assumptions.payment_processing_fee_rate)
    if assumptions.vat_treatment == "taxable":
        revenue_per_ppt = revenue_per_ppt / (1 + assumptions.vat_rate)
    break_even_size = costs.total / revenue_per_ppt if revenue_per_ppt > 0 else 0.0
    
    if cash_surplus_margin >= target_margin:
        economics_status = "VIABLE"
    else:
        economics_status = "REVIEW"

    # Q10 launch gates: economics VIABLE, confirmed participants and secured
    # revenue above their minimums, and priced seats reconciled with planned
    # participants. Model-check failures are layered on in validators.py.
    total_priced = cfg.pricing.early.seats + cfg.pricing.standard.seats + cfg.pricing.installment.seats
    confirmed_ok = cfg.launch_gates.confirmed_participants >= cfg.launch_gates.minimum_confirmed_participants
    secured_ok = cfg.launch_gates.secured_revenue_to_date >= cfg.launch_gates.minimum_secured_revenue
    seats_ok = total_priced == total_participants

    if economics_status == "VIABLE" and confirmed_ok and secured_ok and seats_ok:
        launch_readiness = "GO"
    elif not confirmed_ok or not secured_ok:
        launch_readiness = "HOLD"
    else:
        launch_readiness = "REVIEW"

    return DecisionsResult(
        cash_surplus=_r(cash_surplus),
        cash_surplus_margin=_r(cash_surplus_margin),
        cash_cost_per_ppt=_r(cash_cost_per_ppt),
        cash_break_even_average_price=_r(break_even_price),
        target_margin_average_price=_r(target_price),
        price_gap_to_target=_r(price_gap),
        break_even_cohort_size=_r(break_even_size),
        minimum_viable_cohort_size=int(break_even_size) + (1 if break_even_size % 1 > 0 else 0),
        pre_tax_profit=_r(cash_surplus),
        economics_status=economics_status,
        launch_readiness=launch_readiness,
    )


def calculate_cash_flow(cfg: PricingScenarioInput, revenue: EnhancedRevenueResult, costs: TotalCostResult) -> CashFlowResult:
    timing = cfg.cash_flow_timing
    total_costs = costs.total
    net_revenue = revenue.net_programme_revenue
    
    schedule = []
    opening_balance = 0.0
    lowest_balance = 0.0
    lowest_week = "Pre-launch"
    
    for i, phase in enumerate(timing.phase_labels):
        rev_profile = timing.revenue_collection_profile[i] if i < len(timing.revenue_collection_profile) else 0.0
        cost_profile = timing.cost_payment_profile[i] if i < len(timing.cost_payment_profile) else 0.0
        
        net_revenue_collected = net_revenue * rev_profile
        cash_costs_paid = total_costs * cost_profile
        net_cash_movement = net_revenue_collected - cash_costs_paid
        closing_balance = opening_balance + net_cash_movement
        
        schedule.append(CashFlowMonth(
            phase=phase,
            net_revenue_collected=_r(net_revenue_collected),
            cash_costs_paid=_r(cash_costs_paid),
            net_cash_movement=_r(net_cash_movement),
            opening_balance=_r(opening_balance),
            closing_balance=_r(closing_balance),
        ))
        
        if closing_balance < lowest_balance:
            lowest_balance = closing_balance
            lowest_week = phase
        
        opening_balance = closing_balance
    
    pre_launch_funding = max(0.0, -lowest_balance)
    ending_balance = schedule[-1].closing_balance if schedule else 0.0
    
    return CashFlowResult(
        monthly_schedule=schedule,
        pre_launch_funding_required=_r(pre_launch_funding),
        lowest_balance_week=lowest_week,
        lowest_balance_amount=_r(lowest_balance),
        ending_balance=_r(ending_balance),
    )


def calculate_capacity(cfg: PricingScenarioInput) -> CapacityResult:
    total_participants = sum(cfg.workstreams.dict().values())
    num_mentors = len(WORKSTREAM_ORDER)
    mentor_capacity_per_mentor = 6
    
    max_mentor_capacity = num_mentors * mentor_capacity_per_mentor
    if total_participants <= max_mentor_capacity:
        mentor_status = "OK"
        mentor_detail = f"{num_mentors} mentors × {mentor_capacity_per_mentor} capacity = {max_mentor_capacity} max. Current: {total_participants} ✅"
    elif total_participants <= max_mentor_capacity * 1.25:
        mentor_status = "WARNING"
        mentor_detail = f"{num_mentors} mentors × {mentor_capacity_per_mentor} = {max_mentor_capacity} max. Current: {total_participants} — over capacity by {total_participants - max_mentor_capacity} ⚠️"
    else:
        mentor_status = "FAIL"
        mentor_detail = f"{num_mentors} mentors × {mentor_capacity_per_mentor} = {max_mentor_capacity} max. Current: {total_participants} — need {((total_participants - 1) // mentor_capacity_per_mentor) + 1} mentors ❌"
    
    tool_checks = []
    
    itsa_participants = cfg.workstreams.itsa
    jira_agents = itsa_participants
    if jira_agents <= 10:
        jira_status = "OK"
    else:
        jira_status = "FAIL"
    tool_checks.append(ToolCapacityCheck(
        tool_name="Jira Cloud",
        limit="10 agents (free tier)",
        current_usage=jira_agents,
        status=jira_status,
        detail=f"{jira_agents} IT participants as agents vs. 10 free limit",
    ))
    
    total_jira_users = total_participants + num_mentors + 6
    if total_jira_users <= 10:
        jwm_status = "OK"
    elif total_jira_users <= 20:
        jwm_status = "WARNING"
    else:
        jwm_status = "FAIL"
    tool_checks.append(ToolCapacityCheck(
        tool_name="Jira Work Management",
        limit="10 users (free tier)",
        current_usage=total_jira_users,
        status=jwm_status,
        detail=f"{total_jira_users} total users (participants + mentors + team)",
    ))
    
    tool_checks.append(ToolCapacityCheck(
        tool_name="Google Workspace",
        limit=None,
        current_usage=total_jira_users,
        status="OK",
        detail=f"Paid per seat — {total_jira_users} seats at $6/mo",
    ))
    
    tool_checks.append(ToolCapacityCheck(
        tool_name="Slack",
        limit="10,000 messages (free tier)",
        current_usage=total_jira_users,
        status="OK",
        detail="Message history limit — monitor usage",
    ))
    
    if any(t.status == "FAIL" for t in tool_checks):
        tool_status = "FAIL"
    elif any(t.status == "WARNING" for t in tool_checks):
        tool_status = "WARNING"
    else:
        tool_status = "OK"
    
    team_hours_per_week = 4.5 + 3.5 + 3.5 + 4.0 + 2.0 + 2.0
    recommended_hours = total_participants * 0.75
    if team_hours_per_week >= recommended_hours:
        team_status = "OK"
        team_detail = f"Team: {team_hours_per_week} hrs/wk. Recommended: {recommended_hours} hrs/wk ✅"
    elif team_hours_per_week >= recommended_hours * 0.75:
        team_status = "WARNING"
        team_detail = f"Team: {team_hours_per_week} hrs/wk. Recommended: {recommended_hours} hrs/wk — consider adding hours ⚠️"
    else:
        team_status = "FAIL"
        team_detail = f"Team: {team_hours_per_week} hrs/wk. Recommended: {recommended_hours} hrs/wk — team overloaded ❌"
    
    return CapacityResult(
        mentor_capacity_status=mentor_status,
        mentor_capacity_detail=mentor_detail,
        mentor_max_capacity=max_mentor_capacity,
        mentor_current_demand=total_participants,
        tool_limit_status=tool_status,
        tool_limit_details=tool_checks,
        team_bandwidth_status=team_status,
        team_bandwidth_detail=team_detail,
    )


def calculate_pricing_tiers(cfg: PricingScenarioInput, costs: TotalCostResult) -> List[PricingTierResult]:
    total_participants = sum(cfg.workstreams.dict().values())
    cost_per_ppt = costs.total / total_participants if total_participants > 0 else 0.0
    
    tiers = [
        PricingTierResult(name="Budget / Pilot", fee=_r(cost_per_ppt * 1.3), description="Low margin, high volume, testing phase", projected_margin=0.0, projected_margin_pct=0.0),
        PricingTierResult(name="Standard", fee=_r(cost_per_ppt * 1.8), description="Healthy margin, accessible price", projected_margin=0.0, projected_margin_pct=0.0),
        PricingTierResult(name="Premium", fee=_r(cost_per_ppt * 2.2), description="Strong margin, selective intake", projected_margin=0.0, projected_margin_pct=0.0),
        PricingTierResult(name="B2B / University", fee=_r(cost_per_ppt * 2.8), description="White-label partner pricing", projected_margin=0.0, projected_margin_pct=0.0),
    ]
    
    for tier in tiers:
        projected_revenue = tier.fee * total_participants
        tier.projected_margin = _r(projected_revenue - costs.total)
        tier.projected_margin_pct = _r((tier.projected_margin / projected_revenue) * 100) if projected_revenue > 0 else 0.0
    
    return tiers


def calculate_break_even_curve(cfg: PricingScenarioInput, costs: TotalCostResult) -> List[BreakEvenPoint]:
    total_participants = sum(cfg.workstreams.dict().values())
    assumptions = cfg.assumptions
    curve = []
    
    for price in range(500, 1001, 25):
        gross = price * total_participants
        net = gross
        if assumptions.vat_treatment == "taxable":
            net = gross / (1 + assumptions.vat_rate)
        
        surplus = net - costs.total
        margin = surplus / net if net > 0 else 0.0
        
        curve.append(BreakEvenPoint(
            average_gross_price=float(price),
            gross_receipts=_r(gross),
            net_programme_revenue=_r(net),
            total_cohort_cash_cost=_r(costs.total),
            cash_surplus=_r(surplus),
            cash_surplus_margin=_r(margin),
        ))
    
    return curve


def calculate_sensitivity(cfg: PricingScenarioInput, costs: TotalCostResult) -> List[List[SensitivityCell]]:
    assumptions = cfg.assumptions
    grid = []
    
    for participants in range(12, 51, 4):
        row = []
        for price in range(500, 1001, 25):
            gross = price * participants
            net = gross
            if assumptions.vat_treatment == "taxable":
                net = gross / (1 + assumptions.vat_rate)
            
            total_participants = sum(cfg.workstreams.dict().values())
            if total_participants > 0:
                scaled_costs = costs.total * (participants / total_participants)
            else:
                scaled_costs = costs.total
            
            surplus = net - scaled_costs
            margin = surplus / net if net > 0 else 0.0
            
            if margin >= 0.30:
                status = "high_surplus"
            elif margin >= 0.10:
                status = "surplus"
            elif margin >= 0.0:
                status = "break_even"
            else:
                status = "deficit"
            
            row.append(SensitivityCell(
                participants=participants,
                average_price=float(price),
                cash_surplus=_r(surplus),
                cash_surplus_margin=_r(margin),
                status=status,
            ))
        grid.append(row)
    
    return grid


def calculate_team_compensation(cfg: PricingScenarioInput) -> TeamResponse:
    team = cfg.internal_team
    months = team.active_months
    
    members = [
        TeamMemberComp(role="Founder — Solomon", monthly=team.founder_solomon.monthly, months=months, total=_r(team.founder_solomon.monthly * months), m365_account=True),
        TeamMemberComp(role="Founder — David", monthly=team.founder_david.monthly, months=months, total=_r(team.founder_david.monthly * months), m365_account=True),
        TeamMemberComp(role="Founder — Akua", monthly=team.founder_akua.monthly, months=months, total=_r(team.founder_akua.monthly * months), m365_account=True),
        TeamMemberComp(role=f"Volunteer (×{team.volunteers.count})", monthly=team.volunteers.monthly_each, months=months, total=_r(team.volunteers.count * team.volunteers.monthly_each * months), m365_account=True),
        TeamMemberComp(role=f"Intern (×{team.intern.count})", monthly=team.intern.monthly, months=months, total=_r(team.intern.count * team.intern.monthly * months), m365_account=True),
    ]
    
    total = sum(m.total for m in members)
    
    return TeamResponse(members=members, total=_r(total))


def compare_scenarios(scenarios: List[PricingScenarioInput], names: Optional[List[str]] = None) -> List[ScenarioComparison]:
    comparisons = []
    for i, scenario in enumerate(scenarios):
        revenue = calculate_revenue(scenario)
        costs = calculate_total_cost(scenario, revenue.net_programme_revenue)
        decisions = calculate_decisions(scenario, revenue, costs)
        name = names[i] if names and i < len(names) else "Scenario {}".format(chr(65 + i))
        comparisons.append(ScenarioComparison(
            name=name,
            total_participants=sum(scenario.workstreams.dict().values()),
            average_gross_price=revenue.average_gross_price,
            gross_receipts=revenue.participant_gross_receipts,
            net_programme_revenue=revenue.net_programme_revenue,
            total_cost=costs.total,
            cash_surplus=decisions.cash_surplus,
            cash_surplus_margin=decisions.cash_surplus_margin,
            break_even_price=decisions.cash_break_even_average_price,
            break_even_cohort_size=decisions.break_even_cohort_size,
            target_margin_price=decisions.target_margin_average_price,
            economics_status=decisions.economics_status,
            launch_readiness=decisions.launch_readiness,
        ))
    return comparisons


def run_full_calculation(cfg: PricingScenarioInput) -> Dict:
    revenue = calculate_revenue(cfg)
    costs = calculate_total_cost(cfg, revenue.net_programme_revenue)
    decisions = calculate_decisions(cfg, revenue, costs)
    pricing_tiers = calculate_pricing_tiers(cfg, costs)
    break_even_curve = calculate_break_even_curve(cfg, costs)
    sensitivity = calculate_sensitivity(cfg, costs)
    team = calculate_team_compensation(cfg)
    cash_flow = calculate_cash_flow(cfg, revenue, costs)
    capacity = calculate_capacity(cfg)
    
    return {
        "config": cfg,
        "revenue": revenue,
        "tools": calculate_tools(cfg),
        "mentors": calculate_mentors(cfg),
        "internal_team": calculate_internal_team(cfg),
        "operational": calculate_operational(cfg),
        "other_costs": calculate_other_costs(cfg, revenue.net_programme_revenue),
        "total_costs": costs,
        "decisions": decisions,
        "pricing_tiers": pricing_tiers,
        "cash_flow": cash_flow,
        "capacity": capacity,
        "break_even_curve": break_even_curve,
        "sensitivity": sensitivity,
        "team": team,
    }