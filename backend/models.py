"""backend/models.py — Pydantic v1 schemas for CareerLeap Pricing Dashboard v5.1
Extends v5.0 with fields for all 10 business questions.
"""
from typing import Optional, List, Dict
from pydantic import BaseModel, Field


# ─── INPUT MODELS ────────────────────────────────────────────────────────────

class Assumptions(BaseModel):
    tool_access_period_months: int = Field(default=5, ge=1, le=24)
    contingency_rate: float = Field(default=0.15, ge=0.0, le=1.0)
    mentor_hours_per_week: float = Field(default=4.0, ge=0.0)
    mentor_delivery_weeks: int = Field(default=15, ge=1, le=52)
    mentor_hourly_rate_eur: float = Field(default=20.0, ge=0.0)
    internal_team_active_months: int = Field(default=5, ge=1, le=24)
    usd_to_eur_rate: float = Field(default=0.86, ge=0.01)
    vat_rate: float = Field(default=0.19, ge=0.0, le=1.0)
    vat_treatment: str = Field(default="small_business")
    payment_processing_fee_rate: float = Field(default=0.023, ge=0.0, le=1.0)
    displayed_price_includes_vat: bool = Field(default=True)
    target_cash_surplus_margin: float = Field(default=0.05, ge=0.0, le=1.0)
    down_payment_rate: float = Field(default=0.30, ge=0.0, le=1.0)


class WorkstreamConfig(BaseModel):
    itsa: int = Field(default=10, ge=0)
    data: int = Field(default=10, ge=0)
    marketing: int = Field(default=10, ge=0)
    product: int = Field(default=10, ge=0)


class ToolMatrix(BaseModel):
    jira_cloud: float = Field(default=0.0)
    jira_work_mgmt: float = Field(default=8.0)
    google_workspace: float = Field(default=6.0)
    google_cloud: float = Field(default=0.0)
    password_mgr: float = Field(default=5.0)
    slack: float = Field(default=0.0)
    dbt_core: float = Field(default=0.0)
    postgresql: float = Field(default=0.0)
    motherduck: float = Field(default=0.0)
    superset: float = Field(default=0.0)
    github_actions: float = Field(default=0.0)
    webflow: float = Field(default=0.0)
    ghost: float = Field(default=0.0)
    figma: float = Field(default=0.0)
    beehiiv: float = Field(default=0.0)
    canva: float = Field(default=0.0)
    google_analytics: float = Field(default=0.0)


class ToolsConfig(BaseModel):
    itsa: ToolMatrix = Field(default_factory=ToolMatrix)
    data: ToolMatrix = Field(default_factory=lambda: ToolMatrix(google_cloud=8.0))
    marketing: ToolMatrix = Field(default_factory=lambda: ToolMatrix(webflow=18.0, ghost=9.0))
    product: ToolMatrix = Field(default_factory=ToolMatrix)


class FounderSpec(BaseModel):
    monthly: float = Field(default=500.0, ge=0.0)


class VolunteersSpec(BaseModel):
    count: int = Field(default=2, ge=0)
    monthly_each: float = Field(default=218.72, ge=0.0)


class InternSpec(BaseModel):
    count: int = Field(default=1, ge=0)
    monthly: float = Field(default=218.60, ge=0.0)


class InternalTeamConfig(BaseModel):
    active_months: int = Field(default=5, ge=1)
    founder_solomon: FounderSpec = Field(default_factory=FounderSpec)
    founder_david: FounderSpec = Field(default_factory=FounderSpec)
    founder_akua: FounderSpec = Field(default_factory=FounderSpec)
    volunteers: VolunteersSpec = Field(default_factory=VolunteersSpec)
    intern: InternSpec = Field(default_factory=InternSpec)


class OperationalItem(BaseModel):
    cost_basis: str = Field(default="per_user_month")
    unit_cost: float = Field(default=0.0, ge=0.0)
    quantity: int = Field(default=0, ge=0)
    active_months: int = Field(default=5, ge=1)


class OperationalConfig(BaseModel):
    notion: OperationalItem = Field(default_factory=lambda: OperationalItem(cost_basis="per_user_month", unit_cost=13.68, quantity=4, active_months=5))
    render: OperationalItem = Field(default_factory=lambda: OperationalItem(cost_basis="fixed_month", unit_cost=15.38, quantity=1, active_months=5))
    resend: OperationalItem = Field(default_factory=lambda: OperationalItem(cost_basis="fixed_month", unit_cost=0.0, quantity=1, active_months=5))
    calendly: OperationalItem = Field(default_factory=lambda: OperationalItem(cost_basis="fixed_month", unit_cost=0.0, quantity=1, active_months=5))
    aws: OperationalItem = Field(default_factory=lambda: OperationalItem(cost_basis="fixed_month", unit_cost=0.0, quantity=1, active_months=5))
    bitwarden: OperationalItem = Field(default_factory=lambda: OperationalItem(cost_basis="per_user_month", unit_cost=3.42, quantity=6, active_months=5))
    namecheap: OperationalItem = Field(default_factory=lambda: OperationalItem(cost_basis="fixed_annual", unit_cost=100.0, quantity=1, active_months=5))


class OtherCostItem(BaseModel):
    amount: float = Field(default=0.0, ge=0.0)
    is_percentage_of_revenue: bool = Field(default=False)
    percentage_rate: Optional[float] = Field(default=None)


class OtherCostsConfig(BaseModel):
    legal_review: OtherCostItem = Field(default_factory=OtherCostItem)
    tax_adviser: OtherCostItem = Field(default_factory=OtherCostItem)
    bookkeeping: OtherCostItem = Field(default_factory=lambda: OtherCostItem(amount=0.0))
    payment_processing: OtherCostItem = Field(default_factory=lambda: OtherCostItem(is_percentage_of_revenue=True, percentage_rate=0.023))
    insurance: OtherCostItem = Field(default_factory=OtherCostItem)
    recruitment_marketing: OtherCostItem = Field(default_factory=OtherCostItem)
    refund_reserve: OtherCostItem = Field(default_factory=lambda: OtherCostItem(is_percentage_of_revenue=True, percentage_rate=0.0))
    gdpr_review: OtherCostItem = Field(default_factory=OtherCostItem)
    certificates: OtherCostItem = Field(default_factory=OtherCostItem)
    travel_venue: OtherCostItem = Field(default_factory=OtherCostItem)
    bank_charges: OtherCostItem = Field(default_factory=OtherCostItem)
    accreditation: OtherCostItem = Field(default_factory=OtherCostItem)


class PricingTier(BaseModel):
    seats: int = Field(default=0, ge=0)
    price: float = Field(default=0.0, ge=0.0)


class PricingConfig(BaseModel):
    early: PricingTier = Field(default_factory=lambda: PricingTier(seats=6, price=649.0))
    standard: PricingTier = Field(default_factory=lambda: PricingTier(seats=10, price=699.0))
    installment: PricingTier = Field(default_factory=lambda: PricingTier(seats=4, price=720.0))


class LaunchGates(BaseModel):
    confirmed_participants: int = Field(default=0, ge=0)
    minimum_confirmed_participants: int = Field(default=16, ge=0)
    secured_revenue_to_date: float = Field(default=0.0, ge=0.0)
    minimum_secured_revenue: float = Field(default=10000.0, ge=0.0)


class CashFlowTiming(BaseModel):
    revenue_collection_profile: List[float] = Field(default_factory=lambda: [0.40, 0.25, 0.20, 0.10, 0.05])
    cost_payment_profile: List[float] = Field(default_factory=lambda: [0.25, 0.25, 0.20, 0.20, 0.10])
    phase_labels: List[str] = Field(default_factory=lambda: ["Pre-launch", "Month 1", "Month 2", "Month 3", "Extension"])


class PricingScenarioInput(BaseModel):
    assumptions: Assumptions = Field(default_factory=Assumptions)
    workstreams: WorkstreamConfig = Field(default_factory=WorkstreamConfig)
    tools: ToolsConfig = Field(default_factory=ToolsConfig)
    internal_team: InternalTeamConfig = Field(default_factory=InternalTeamConfig)
    operational: OperationalConfig = Field(default_factory=OperationalConfig)
    other_costs: OtherCostsConfig = Field(default_factory=OtherCostsConfig)
    pricing: PricingConfig = Field(default_factory=PricingConfig)
    launch_gates: LaunchGates = Field(default_factory=LaunchGates)
    cash_flow_timing: CashFlowTiming = Field(default_factory=CashFlowTiming)


# ─── OUTPUT MODELS ───────────────────────────────────────────────────────────

class RevenueBridgeItem(BaseModel):
    label: str
    amount: float
    operation: str


class EnhancedRevenueResult(BaseModel):
    participant_gross_receipts: float
    vat_payable: float
    net_programme_revenue: float
    average_gross_price: float
    average_net_price: float
    immediate_receipts: float
    deferred_receipts: float
    revenue_bridge: List[RevenueBridgeItem] = Field(default_factory=list)


class WorkstreamToolCost(BaseModel):
    monthly_per_ppt_usd: float
    base_per_ppt_usd: float
    contingency_per_ppt_usd: float
    total_per_ppt_usd: float
    total_per_ppt_eur: float
    workstream_total_usd: float
    workstream_total_eur: float


class ToolsResult(BaseModel):
    total_tools_usd: float
    total_tools_eur: float
    workstream_breakdown: Dict[str, WorkstreamToolCost]


class MentorsResult(BaseModel):
    total: float
    per_participant: float
    breakdown: Dict[str, float]


class InternalTeamResult(BaseModel):
    total: float
    per_participant: float
    breakdown: Dict[str, float]


class OperationalResult(BaseModel):
    total: float
    per_participant: float
    breakdown: Dict[str, float]


class OtherCostsResult(BaseModel):
    total: float
    per_participant: float
    breakdown: Dict[str, float]


class CostLineItem(BaseModel):
    category: str
    subcategory: Optional[str] = None
    amount_eur: float
    amount_usd: Optional[float] = None
    basis: str


class TotalCostResult(BaseModel):
    tools_eur: float
    mentors: float
    internal_team: float
    operational: float
    other: float
    total: float
    per_participant: float
    line_items: List[CostLineItem] = Field(default_factory=list)
    per_participant_breakdown: Dict[str, float] = Field(default_factory=dict)
    per_participant_by_workstream: Dict[str, float] = Field(default_factory=dict)
    cost_by_workstream: Dict[str, float] = Field(default_factory=dict)


class CashFlowMonth(BaseModel):
    phase: str
    net_revenue_collected: float
    cash_costs_paid: float
    net_cash_movement: float
    opening_balance: float
    closing_balance: float


class CashFlowResult(BaseModel):
    monthly_schedule: List[CashFlowMonth] = Field(default_factory=list)
    pre_launch_funding_required: float
    lowest_balance_week: str
    lowest_balance_amount: float
    ending_balance: float


class ToolCapacityCheck(BaseModel):
    tool_name: str
    limit: Optional[str]
    current_usage: int
    status: str
    detail: str


class CapacityResult(BaseModel):
    mentor_capacity_status: str
    mentor_capacity_detail: str
    mentor_max_capacity: int
    mentor_current_demand: int
    tool_limit_status: str
    tool_limit_details: List[ToolCapacityCheck]
    team_bandwidth_status: str
    team_bandwidth_detail: str


class DecisionsResult(BaseModel):
    cash_surplus: float
    cash_surplus_margin: float
    cash_cost_per_ppt: float
    cash_break_even_average_price: float
    target_margin_average_price: float
    price_gap_to_target: float
    break_even_cohort_size: float
    minimum_viable_cohort_size: int
    pre_tax_profit: Optional[float] = None
    economics_status: str
    launch_readiness: str


class PricingTierResult(BaseModel):
    name: str
    fee: float
    description: str
    projected_margin: float
    projected_margin_pct: float


class SensitivityCell(BaseModel):
    participants: int
    average_price: float
    cash_surplus: float
    cash_surplus_margin: float
    status: str


class BreakEvenPoint(BaseModel):
    average_gross_price: float
    gross_receipts: float
    net_programme_revenue: float
    total_cohort_cash_cost: float
    cash_surplus: float
    cash_surplus_margin: float


class TeamMemberComp(BaseModel):
    role: str
    monthly: float
    months: int
    total: float
    m365_account: bool


class CalculateResponse(BaseModel):
    config: PricingScenarioInput
    revenue: EnhancedRevenueResult
    tools: ToolsResult
    mentors: MentorsResult
    internal_team: InternalTeamResult
    operational: OperationalResult
    other_costs: OtherCostsResult
    total_costs: TotalCostResult
    decisions: DecisionsResult
    pricing_tiers: List[PricingTierResult]
    cash_flow: Optional[CashFlowResult] = None
    capacity: Optional[CapacityResult] = None


class SummaryResponse(BaseModel):
    total_participants: int
    total_revenue: float
    total_cost: float
    net_margin: float
    margin_pct: float
    cost_per_participant: float
    profit_per_participant: float
    break_even_price: float
    break_even_cohort_size: float
    target_margin_price: float
    launch_status: str

class ModelCheck(BaseModel):
    name: str
    actual: str
    expected: str
    difference: str
    tolerance: str
    status: str
    where_to_fix: str
    why_it_matters: str

class ChecksResponse(BaseModel):
    checks: List[ModelCheck]
    overall_status: str
    launch_readiness: str
    launch_gates_status: Dict[str, str] = Field(default_factory=dict)
    blocking_gates: List[str] = Field(default_factory=list)


class ModelCheck(BaseModel):
    name: str
    actual: str
    expected: str
    difference: str
    tolerance: str
    status: str
    where_to_fix: str
    why_it_matters: str


class BreakEvenResponse(BaseModel):
    current_model: Dict
    curve: List[BreakEvenPoint]
    cash_break_even_price: float
    target_margin_price: float
    gap_current_vs_break_even: float


class SensitivityResponse(BaseModel):
    current_reference: Dict
    grid: List[List[SensitivityCell]]
    break_even_prices: List[Dict]
    controls: Dict


class TeamResponse(BaseModel):
    members: List[TeamMemberComp]
    total: float


# ─── Q8: SCENARIO COMPARISON ─────────────────────────────────────────────────

class ScenarioComparison(BaseModel):
    name: str
    total_participants: int
    average_gross_price: float
    gross_receipts: float
    net_programme_revenue: float
    total_cost: float
    cash_surplus: float
    cash_surplus_margin: float
    break_even_price: float
    break_even_cohort_size: float
    target_margin_price: float
    economics_status: str
    launch_readiness: str


class ScenarioCompareRequest(BaseModel):
    scenarios: List[PricingScenarioInput]
    names: Optional[List[str]] = None


class ScenarioCompareResponse(BaseModel):
    comparisons: List[ScenarioComparison]


FullCalculateResponse = CalculateResponse

class DefaultsResponse(BaseModel):
    """Legacy response for /api/config/defaults"""
    defaults: PricingScenarioInput

class SummaryRequest(BaseModel):
    """Legacy request wrapper"""
    config: PricingScenarioInput

FullCalculateResponse = CalculateResponse