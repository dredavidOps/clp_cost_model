"""
CareerLeap v5 Cohort Economics Engine
Replicates the Excel v4.0 Simulator/Calculations logic.
"""

import math
from decimal import Decimal, ROUND_HALF_UP
from typing import List

from backend.models import (
    CohortConfigInput,
    RevenueBreakdown,
    CostBreakdown,
    DecisionOutputs,
    AnnualProjectionData,
    PricingTier,
    SensitivityData,
    ToolBreakdownItem,
)


class CohortEngine:
    """Calculates cohort economics from a v5 CohortConfigInput."""

    def __init__(self, config: CohortConfigInput):
        self.config = config
        self.revenue = self._calculate_revenue()
        self.costs = self._calculate_costs()
        self.decisions = self._calculate_decisions()

    # ─── PARTICIPANTS ─────────────────────────────────────────────────────────

    def total_participants(self) -> int:
        ws = self.config.workstreams
        return ws.it_systems_admin + ws.data_bi_ai + ws.product_project_ops + ws.digital_marketing_growth

    def per_workstream_participants(self) -> dict:
        ws = self.config.workstreams
        return {
            "it_systems_admin": ws.it_systems_admin,
            "data_bi_ai": ws.data_bi_ai,
            "product_project_ops": ws.product_project_ops,
            "digital_marketing_growth": ws.digital_marketing_growth,
        }

    # ─── REVENUE ──────────────────────────────────────────────────────────────

    def _calculate_revenue(self) -> RevenueBreakdown:
        sm = self.config.seat_mix
        gross = (
            sm.early_payment_seats * sm.early_payment_price
            + sm.standard_payment_seats * sm.standard_payment_price
            + sm.installment_seats * sm.installment_price
        )
        participants = self.total_participants()

        if self.config.vat_applies:
            vat = gross * self.config.vat_rate / (1 + self.config.vat_rate)
        else:
            vat = 0.0

        net = gross - vat
        avg_gross = gross / participants if participants else 0.0
        avg_net = net / participants if participants else 0.0

        return RevenueBreakdown(
            participant_gross_receipts=round(gross, 2),
            vat_payable=round(vat, 2),
            net_programme_revenue=round(net, 2),
            average_gross_price_per_participant=round(avg_gross, 2),
            average_net_price_per_participant=round(avg_net, 2),
        )

    # ─── COSTS ───────────────────────────────────────────────────────────────

    def required_mentors(self) -> int:
        ws = self.config.workstreams
        cap = self.config.mentor_capacity_per_mentor
        return (
            math.ceil(ws.it_systems_admin / cap)
            + math.ceil(ws.data_bi_ai / cap)
            + math.ceil(ws.product_project_ops / cap)
            + math.ceil(ws.digital_marketing_growth / cap)
        )

    def mentor_cost(self) -> float:
        mentors = self.required_mentors()
        hours_per_week = (
            self.config.mentor_contact_hours_per_week
            + self.config.mentor_prep_hours_per_week
        )
        contact_hours = mentors * hours_per_week * self.config.delivery_weeks
        setup_hours = mentors * self.config.mentor_setup_hours
        total_hours = contact_hours + setup_hours
        return total_hours * self.config.mentor_hourly_rate

    def m365_billing_months(self) -> int:
        total_weeks = (
            self.config.delivery_weeks
            + self.config.m365_access_before_launch_weeks
            + self.config.extension_wrapup_weeks
        )
        return math.ceil(total_weeks / 4)

    def m365_licence_cost(self) -> float:
        participants = self.total_participants()
        mentors = self.required_mentors()
        internal_with_m365 = sum(
            1 for m in self.config.internal_team if m.include and m.m365_account
        )
        extra_accounts = 0
        total_accounts = participants + mentors + internal_with_m365 + extra_accounts
        months = self.m365_billing_months()
        return total_accounts * months * self.config.m365_price_per_account_per_month

    def other_tools_cost(self) -> float:
        """Sum of included tool-registry items."""
        total = 0.0
        for tool in self.config.tools:
            if tool.get("include", True):
                total += tool.get("included_cost", 0.0)
        return total

    def internal_team_payments(self) -> float:
        multiplier = self.config.internal_team_workload_multiplier
        total = 0.0
        for member in self.config.internal_team:
            if member.include:
                total += (
                    member.weekly_hours
                    * member.weeks
                    * member.hourly_rate
                    * multiplier
                )
        return total

    def other_external_costs(self) -> float:
        return sum(
            item.cost for item in self.config.other_external_costs if item.include
        )

    def payment_processing_fees(self) -> float:
        return (
            self.revenue.participant_gross_receipts
            * self.config.payment_processing_fee_rate
        )

    def _calculate_costs(self) -> CostBreakdown:
        mentor = self.mentor_cost()
        m365 = self.m365_licence_cost()
        tools = self.other_tools_cost()
        internal = self.internal_team_payments()
        external = self.other_external_costs()
        payment_fees = self.payment_processing_fees()

        external_before_contingency = mentor + m365 + tools + external + payment_fees
        contingency = float(
            Decimal(str(external_before_contingency * self.config.external_cost_contingency_rate)).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )
        )
        total = external_before_contingency + contingency + internal

        participants = self.total_participants()
        cost_per_participant = total / participants if participants else 0.0

        return CostBreakdown(
            mentor_cost=round(mentor, 2),
            m365_licences=round(m365, 2),
            other_tools=round(tools, 2),
            internal_team_payments=round(internal, 2),
            other_external_costs=round(external, 2),
            payment_processing_fees=round(payment_fees, 2),
            contingency_reserve=contingency,
            total_cohort_cash_cost=round(total, 2),
            cash_cost_per_participant=round(cost_per_participant, 2),
        )

    # ─── DECISIONS ─────────────────────────────────────────────────────────────

    def _external_cost_excl_payment_and_contingency(self) -> float:
        return (
            self.costs.mentor_cost
            + self.costs.m365_licences
            + self.costs.other_tools
            + self.costs.other_external_costs
        )

    def _required_gross_receipts(self, target_margin: float) -> float:
        """
        Solve for gross receipts given a target cash surplus margin.
        G = [E*(1+c) + I] / [(1-m)/(1+r) - f*(1+c)]
        where E = external cost excl payment & contingency,
              I = internal team, c = contingency rate, r = VAT rate, f = payment fee rate.
        """
        cfg = self.config
        E = self._external_cost_excl_payment_and_contingency()
        I = self.costs.internal_team_payments
        c = cfg.external_cost_contingency_rate
        r = cfg.vat_rate if cfg.vat_applies else 0.0
        f = cfg.payment_processing_fee_rate
        m = target_margin

        numerator = E * (1 + c) + I
        denominator = (1 - m) / (1 + r) - f * (1 + c)

        if denominator <= 0:
            return float("inf")
        return numerator / denominator

    def _price_from_gross(self, gross: float) -> float:
        participants = self.total_participants()
        if participants == 0:
            return 0.0
        return gross / participants

    def exact_break_even_price(self) -> float:
        """Return unrounded cash break-even average price."""
        return self._required_gross_receipts(0.0) / self.total_participants()

    def exact_target_margin_price(self) -> float:
        """Return unrounded target-margin average price."""
        return (
            self._required_gross_receipts(self.config.target_cash_surplus_margin)
            / self.total_participants()
        )

    def _calculate_decisions(self) -> DecisionOutputs:
        revenue = self.revenue
        costs = self.costs
        participants = self.total_participants()

        surplus = revenue.net_programme_revenue - costs.total_cohort_cash_cost
        margin = (
            surplus / revenue.net_programme_revenue
            if revenue.net_programme_revenue
            else 0.0
        )

        # Break-even: target margin = 0
        break_even_gross = self._required_gross_receipts(0.0)
        break_even_price = self._price_from_gross(break_even_gross)

        # Target-margin price
        target_gross = self._required_gross_receipts(
            self.config.target_cash_surplus_margin
        )
        target_price = self._price_from_gross(target_gross)

        price_gap = target_price - revenue.average_gross_price_per_participant

        # Minimum additional cash buffer is the shortfall if surplus is negative
        buffer = abs(surplus) if surplus < 0 else 0.0

        # Statuses
        economics_status = (
            "VIABLE" if margin >= self.config.target_cash_surplus_margin else "REVIEW"
        )

        # Launch readiness
        ws = self.config.workstreams
        workstreams_ok = (
            ws.it_systems_admin >= self.config.minimum_per_workstream
            and ws.data_bi_ai >= self.config.minimum_per_workstream
            and ws.product_project_ops >= self.config.minimum_per_workstream
            and ws.digital_marketing_growth >= self.config.minimum_per_workstream
        )
        revenue_ok = (
            self.config.secured_net_revenue_to_date
            >= self.config.minimum_secured_net_revenue
        )
        participants_ok = participants >= self.config.minimum_total_participants
        launch_ready = (
            economics_status == "VIABLE"
            and participants_ok
            and workstreams_ok
            and revenue_ok
        )

        return DecisionOutputs(
            cash_surplus=round(surplus, 2),
            cash_surplus_margin=round(margin, 4),
            cash_break_even_average_price=round(break_even_price, 2),
            target_margin_average_price=round(target_price, 2),
            price_gap_to_target=round(price_gap, 2),
            minimum_additional_cash_buffer=round(buffer, 2),
            projected_economics_status=economics_status,
            actual_launch_readiness="GO" if launch_ready else "HOLD",
        )

    # ─── ANNUAL PROJECTION ────────────────────────────────────────────────────

    def get_annual_projection(self, cohorts_per_year: int = 4) -> AnnualProjectionData:
        participants = self.total_participants()
        return AnnualProjectionData(
            cohorts_per_year=cohorts_per_year,
            total_participants=participants * cohorts_per_year,
            annual_revenue=self.revenue.net_programme_revenue * cohorts_per_year,
            annual_costs=self.costs.total_cohort_cash_cost * cohorts_per_year,
            annual_margin=self.decisions.cash_surplus * cohorts_per_year,
            annual_margin_pct=self.decisions.cash_surplus_margin,
        )

    # ─── PRICING TIERS ────────────────────────────────────────────────────────

    def get_pricing_tiers(self) -> List[PricingTier]:
        cost_per = self.costs.cash_cost_per_participant
        tiers = [
            PricingTier(
                name="Budget / pilot",
                fee=cost_per * 1.3,
                description="Low margin, high volume, testing phase",
            ),
            PricingTier(
                name="Standard",
                fee=cost_per * 1.8,
                description="Healthy margin, accessible price point",
            ),
            PricingTier(
                name="Premium",
                fee=cost_per * 2.2,
                description="Strong margin, selective intake",
            ),
            PricingTier(
                name="B2B / University",
                fee=cost_per * 2.8,
                description="White-label partner pricing",
            ),
        ]
        participants = self.total_participants()
        for t in tiers:
            gross = t.fee * participants
            net = gross - (gross * self.config.vat_rate / (1 + self.config.vat_rate))
            t.projected_margin = net - self.costs.total_cohort_cash_cost
            t.projected_margin_pct = (
                (t.projected_margin / net * 100) if net else 0.0
            )
        return tiers

    # ─── SENSITIVITY (legacy line charts) ───────────────────────────────────────

    def get_sensitivity(self) -> SensitivityData:
        base_avg = self.revenue.average_gross_price_per_participant
        base_participants = self.total_participants()

        fee_range = [-0.2, -0.1, 0, 0.1, 0.2, 0.5, 1.0]
        size_range = [-0.33, -0.2, -0.1, 0, 0.1, 0.33, 1.0]

        fee_points = []
        for pct in fee_range:
            price = base_avg * (1 + pct)
            # quick surplus estimate
            gross = price * base_participants
            net = gross - (gross * self.config.vat_rate / (1 + self.config.vat_rate))
            surplus = net - self.costs.total_cohort_cash_cost
            margin = surplus / net if net else 0.0
            fee_points.append({"value": price, "margin_pct": margin})

        size_points = []
        for pct in size_range:
            size = int(round(base_participants * (1 + pct)))
            if size < 1:
                size = 1
            gross = base_avg * size
            net = gross - (gross * self.config.vat_rate / (1 + self.config.vat_rate))
            # Scale mentor cost roughly with participants
            mentor_ratio = size / base_participants if base_participants else 1.0
            scaled_cost = (
                self.costs.mentor_cost * mentor_ratio
                + self.costs.m365_licences
                + self.costs.other_tools
                + self.costs.internal_team_payments
                + self.costs.other_external_costs
                + self.costs.payment_processing_fees
                + self.costs.contingency_reserve
            )
            surplus = net - scaled_cost
            margin = surplus / net if net else 0.0
            size_points.append({"value": size, "margin_pct": margin})

        return SensitivityData(
            participant_fee=fee_points,
            cohort_size=size_points,
        )

    # ─── TOOL BREAKDOWN ─────────────────────────────────────────────────────────

    def get_tool_breakdown(self) -> List[ToolBreakdownItem]:
        items = []
        for tool in self.config.tools:
            if tool.get("include", True):
                items.append(ToolBreakdownItem(**tool))
        return items
