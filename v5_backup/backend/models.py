from typing import List, Optional
from pydantic import BaseModel, Field


# ─── WORKSTREAM & SEAT MIX ───────────────────────────────────────────────────

class WorkstreamConfig(BaseModel):
    it_systems_admin: int = 5
    data_bi_ai: int = 5
    product_project_ops: int = 5
    digital_marketing_growth: int = 5


class SeatMix(BaseModel):
    early_payment_seats: int = 6
    early_payment_price: float = 649.0
    standard_payment_seats: int = 10
    standard_payment_price: float = 699.0
    installment_seats: int = 4
    installment_price: float = 720.0


# ─── INTERNAL TEAM & EXTERNAL COSTS ────────────────────────────────────────────

class InternalTeamMember(BaseModel):
    id: str
    name: str
    role: str
    weekly_hours: float
    weeks: int
    hourly_rate: float
    include: bool = True
    m365_account: bool = True
    contribution: str = ""


class OtherExternalCost(BaseModel):
    item: str
    include: bool
    cost: float
    priority: str = "Medium"
    explanation: str = ""


# ─── MAIN CONFIGURATION INPUT ─────────────────────────────────────────────────

class CohortConfigInput(BaseModel):
    # Core simulation controls
    workstreams: WorkstreamConfig = Field(default_factory=WorkstreamConfig)
    seat_mix: SeatMix = Field(default_factory=SeatMix)

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

    # Internal team and other external costs (populated from JSON defaults)
    internal_team: List[InternalTeamMember] = Field(default_factory=list)
    other_external_costs: List[OtherExternalCost] = Field(default_factory=list)

    # Tool registry override (loaded from JSON by default)
    tools: List[dict] = Field(default_factory=list)
    m365_price_per_account_per_month: float = 7.28

    # Career track (kept for backward-compatible tool cost mode)
    career_track: str = "it_infrastructure"
    tool_cost_per_user_per_month: Optional[float] = None
    fixed_tool_cost_per_month: Optional[float] = None

    # Legacy fields — ignored by v5 engine but kept for API compatibility
    participant_fee: Optional[float] = None
    cohort_size: Optional[int] = None
    duration_months: Optional[int] = None
    num_leads: Optional[int] = None
    stipend_per_lead: Optional[float] = None
    overhead_per_participant: Optional[float] = 150.0
    placement_bonus_per_lead: float = 0.0
    no_show_rate: float = 0.05
    refund_rate: float = 0.03


# ─── CALCULATE RESPONSE ──────────────────────────────────────────────────────

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
    projected_economics_status: str
    actual_launch_readiness: str


class AnnualProjectionData(BaseModel):
    cohorts_per_year: int
    total_participants: int
    annual_revenue: float
    annual_costs: float
    annual_margin: float
    annual_margin_pct: float


class PricingTier(BaseModel):
    name: str
    fee: float
    description: str
    projected_margin: float = 0.0
    projected_margin_pct: float = 0.0


class SensitivityData(BaseModel):
    participant_fee: List[dict]
    cohort_size: List[dict]


class ToolBreakdownItem(BaseModel):
    scope: Optional[str] = None
    name: str
    category: Optional[str] = None
    billing_model: Optional[str] = None
    cost_per_user_per_month: Optional[float] = None
    cost_total_for_cohort: Optional[float] = None
    unit_cost: Optional[float] = None
    billing_periods: Optional[int] = None
    quantity: Optional[int] = None
    included_cost: Optional[float] = None
    source_id: Optional[str] = None
    delivery_note: Optional[str] = None
    owner: Optional[str] = None
    free_tier_available: bool = False
    free_tier_limit: Optional[str] = None
    why_chosen: Optional[str] = None
    source_url: str = ""
    last_verified: str = ""
    include: bool = True


class CareerTrackOutput(BaseModel):
    key: str
    label: str
    short_name: Optional[str] = None
    role_in_simulation: Optional[str] = None
    skills: List[str] = Field(default_factory=list)
    tools: List[ToolBreakdownItem] = Field(default_factory=list)
    track_total_tool_cost: Optional[float] = None
    track_cost_per_participant: Optional[float] = None
    total_tool_cost_per_user_per_month: Optional[float] = None


class CalculateResponse(BaseModel):
    config: CohortConfigInput
    revenue: RevenueBreakdown
    costs: CostBreakdown
    decisions: DecisionOutputs
    pricing_tiers: List[PricingTier]
    sensitivity: SensitivityData
    annual_projection: AnnualProjectionData
    career_track: Optional[CareerTrackOutput] = None
    tool_breakdown: List[ToolBreakdownItem] = Field(default_factory=list)


# ─── SCENARIOS ───────────────────────────────────────────────────────────────

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
    status: str


class ScenariosResponse(BaseModel):
    conservative: ScenarioResult
    base: ScenarioResult
    growth: ScenarioResult
    custom: ScenarioResult
    custom_name: str = "Custom"


# ─── SENSITIVITY ───────────────────────────────────────────────────────────────

class SensitivityCell(BaseModel):
    participants: int
    average_price: float
    cash_surplus: float
    cash_surplus_margin: float
    status: str


class SensitivityResponse(BaseModel):
    current_reference: dict
    grid: List[List[SensitivityCell]]
    break_even_prices: List[dict]
    controls: dict


# ─── CASH FLOW ─────────────────────────────────────────────────────────────────

class CashFlowMonth(BaseModel):
    phase: str
    net_revenue_collected: float
    cash_costs_paid: float
    net_cash_movement: float
    opening_balance: float
    closing_balance: float


class CashFlowResponse(BaseModel):
    timing_assumptions: dict
    monthly_schedule: List[CashFlowMonth]
    minimum_funding_buffer: float
    lowest_projected_balance: float
    ending_balance: float


# ─── BREAK-EVEN ───────────────────────────────────────────────────────────────

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
    chart_controls: dict


# ─── CHECKS ─────────────────────────────────────────────────────────────────────

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


# ─── TEAM ROSTER & PRICING TIER DEFAULTS ────────────────────────────────────────

class TeamRoster(BaseModel):
    members: List[InternalTeamMember]


class PricingTierDefaults(BaseModel):
    seat_mix: SeatMix
