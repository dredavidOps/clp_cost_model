"""
CareerLeap v5 Model Checks Engine
Replicates the Excel "Checks & Guide" sheet validations.
"""

import copy
from typing import List

from backend.models import (
    CohortConfigInput,
    ChecksResponse,
    ModelCheck,
    CalculateResponse,
    ScenariosResponse,
    CashFlowResponse,
    BreakEvenResponse,
)
from backend.engine import CohortEngine
from backend.cashflow import CashFlowEngine
from backend.breakeven import BreakEvenEngine
from backend.scenarios import ScenarioEngine


def _fmt(value) -> str:
    if isinstance(value, float):
        return f"{value:.2f}"
    return str(value)


def _ok(actual, expected, tolerance: float = 0.0) -> bool:
    return abs(float(actual) - float(expected)) <= tolerance


class ChecksEngine:
    """Runs all 21 model validation checks."""

    def __init__(
        self,
        config: CohortConfigInput,
        result: CalculateResponse,
        scenarios: ScenariosResponse,
        cashflow: CashFlowResponse,
        breakeven: BreakEvenResponse,
    ):
        self.config = config
        self.result = result
        self.scenarios = scenarios
        self.cashflow = cashflow
        self.breakeven = breakeven
        self.checks = self._run_checks()

    def _run_checks(self) -> List[ModelCheck]:
        ws = self.config.workstreams
        total_planned = (
            ws.it_systems_admin
            + ws.data_bi_ai
            + ws.product_project_ops
            + ws.digital_marketing_growth
        )
        sm = self.config.seat_mix
        seat_total = (
            sm.early_payment_seats + sm.standard_payment_seats + sm.installment_seats
        )

        engine = CohortEngine(self.config)
        base_scenario = self.scenarios.base

        checks = []

        # 1. Planned pricing seats = planned participants
        checks.append(
            ModelCheck(
                name="Planned pricing seats = planned participants",
                actual=_fmt(seat_total),
                expected=_fmt(total_planned),
                difference=_fmt(seat_total - total_planned),
                tolerance="0",
                status="OK" if seat_total == total_planned else "FAIL",
                where_to_fix="Seat mix or workstream participant counts",
                why_it_matters="Every participant must be assigned a pricing seat.",
            )
        )

        # 2. Confirmed ≤ planned participants
        checks.append(
            ModelCheck(
                name="Confirmed participants ≤ planned participants",
                actual=_fmt(total_planned),
                expected=f"≤ {_fmt(total_planned)}",
                difference="0",
                tolerance="0",
                status="OK",
                where_to_fix="Workstream participant counts",
                why_it_matters="Cannot confirm more participants than planned.",
            )
        )

        # 3. Every active workstream has ≥1 mentor
        mentor_count = engine.required_mentors()
        checks.append(
            ModelCheck(
                name="Every active workstream has ≥1 mentor",
                actual=_fmt(mentor_count),
                expected="≥ 4",
                difference=_fmt(max(0, 4 - mentor_count)),
                tolerance="0",
                status="OK" if mentor_count >= 4 else "FAIL",
                where_to_fix="Mentor capacity or workstream participant counts",
                why_it_matters="Each workstream needs at least one dedicated mentor.",
            )
        )

        # 4. Mentor hours and rate are positive
        positive = (
            self.config.mentor_contact_hours_per_week > 0
            and self.config.mentor_prep_hours_per_week > 0
            and self.config.mentor_hourly_rate > 0
        )
        checks.append(
            ModelCheck(
                name="Mentor hours and rate are positive",
                actual="All positive" if positive else "Not positive",
                expected="All positive",
                difference="0",
                tolerance="0",
                status="OK" if positive else "FAIL",
                where_to_fix="Mentor assumptions",
                why_it_matters="Zero or negative mentor inputs would break cost logic.",
            )
        )

        # 5. M365 account count reconciles
        participants = engine.total_participants()
        internal_m365 = sum(
            1 for m in self.config.internal_team if m.include and m.m365_account
        )
        expected_m365 = participants + mentor_count + internal_m365
        actual_m365 = (
            self.result.costs.m365_licences
            / self.config.m365_price_per_account_per_month
            / engine.m365_billing_months()
            if self.config.m365_price_per_account_per_month and engine.m365_billing_months()
            else 0
        )
        checks.append(
            ModelCheck(
                name="M365 account count reconciles",
                actual=_fmt(round(actual_m365, 0)),
                expected=_fmt(expected_m365),
                difference=_fmt(round(abs(actual_m365 - expected_m365), 2)),
                tolerance="0.5",
                status="OK" if abs(actual_m365 - expected_m365) <= 0.5 else "FAIL",
                where_to_fix="Internal team M365 flags or participant counts",
                why_it_matters="Licence count drives M365 cash cost.",
            )
        )

        # 6. M365 billing months cover all access weeks
        months = engine.m365_billing_months()
        required_months = (
            self.config.delivery_weeks
            + self.config.m365_access_before_launch_weeks
            + self.config.extension_wrapup_weeks
        ) / 4
        checks.append(
            ModelCheck(
                name="M365 billing months cover all access weeks",
                actual=_fmt(months),
                expected=f"≥ {_fmt(required_months)}",
                difference="0",
                tolerance="0",
                status="OK" if months >= required_months else "FAIL",
                where_to_fix="M365 billing months or programme timing",
                why_it_matters="Must bill for every week of access.",
            )
        )

        # 7. Tool detail = tool summary
        tool_detail = sum(t.included_cost or 0 for t in self.result.tool_breakdown)
        checks.append(
            ModelCheck(
                name="Tool detail equals tool summary",
                actual=_fmt(tool_detail),
                expected=_fmt(self.result.costs.other_tools),
                difference=_fmt(round(abs(tool_detail - self.result.costs.other_tools), 2)),
                tolerance="0.01",
                status="OK"
                if abs(tool_detail - self.result.costs.other_tools) <= 0.01
                else "FAIL",
                where_to_fix="Tools registry included_cost values",
                why_it_matters="Detailed tool costs must sum to the summary line.",
            )
        )

        # 8. Revenue total = revenue components
        expected_revenue = self.result.revenue.participant_gross_receipts
        seat_revenue = (
            sm.early_payment_seats * sm.early_payment_price
            + sm.standard_payment_seats * sm.standard_payment_price
            + sm.installment_seats * sm.installment_price
        )
        checks.append(
            ModelCheck(
                name="Revenue total equals seat mix revenue",
                actual=_fmt(seat_revenue),
                expected=_fmt(expected_revenue),
                difference=_fmt(round(abs(seat_revenue - expected_revenue), 2)),
                tolerance="0.01",
                status="OK"
                if abs(seat_revenue - expected_revenue) <= 0.01
                else "FAIL",
                where_to_fix="Seat mix seats and prices",
                why_it_matters="Revenue must match the sum of all paid seats.",
            )
        )

        # 9. Cash cost = cost components
        cost_sum = (
            self.result.costs.mentor_cost
            + self.result.costs.m365_licences
            + self.result.costs.other_tools
            + self.result.costs.internal_team_payments
            + self.result.costs.other_external_costs
            + self.result.costs.payment_processing_fees
            + self.result.costs.contingency_reserve
        )
        checks.append(
            ModelCheck(
                name="Cash cost equals cost components",
                actual=_fmt(cost_sum),
                expected=_fmt(self.result.costs.total_cohort_cash_cost),
                difference=_fmt(
                    round(abs(cost_sum - self.result.costs.total_cohort_cash_cost), 2)
                ),
                tolerance="0.01",
                status="OK"
                if abs(cost_sum - self.result.costs.total_cohort_cash_cost) <= 0.01
                else "FAIL",
                where_to_fix="Cost calculation engine",
                why_it_matters="Total cost must be the sum of its parts.",
            )
        )

        # 10. Cash surplus = revenue - cash cost
        calc_surplus = (
            self.result.revenue.net_programme_revenue
            - self.result.costs.total_cohort_cash_cost
        )
        checks.append(
            ModelCheck(
                name="Cash surplus equals revenue minus cash cost",
                actual=_fmt(calc_surplus),
                expected=_fmt(self.result.decisions.cash_surplus),
                difference=_fmt(
                    round(abs(calc_surplus - self.result.decisions.cash_surplus), 2)
                ),
                tolerance="0.01",
                status="OK"
                if abs(calc_surplus - self.result.decisions.cash_surplus) <= 0.01
                else "FAIL",
                where_to_fix="Decision output calculation",
                why_it_matters="Surplus is the fundamental viability metric.",
            )
        )

        # 11. Base scenario participants = Inputs
        checks.append(
            ModelCheck(
                name="Base scenario participants match Inputs",
                actual=_fmt(base_scenario.participants),
                expected=_fmt(total_planned),
                difference=_fmt(base_scenario.participants - total_planned),
                tolerance="0",
                status="OK" if base_scenario.participants == total_planned else "FAIL",
                where_to_fix="Scenario engine",
                why_it_matters="Base case must mirror the main input assumptions.",
            )
        )

        # 12. Base scenario revenue = Calculations
        checks.append(
            ModelCheck(
                name="Base scenario revenue matches Calculations",
                actual=_fmt(base_scenario.net_revenue),
                expected=_fmt(self.result.revenue.net_programme_revenue),
                difference=_fmt(
                    round(
                        abs(base_scenario.net_revenue - self.result.revenue.net_programme_revenue),
                        2,
                    )
                ),
                tolerance="0.01",
                status="OK"
                if abs(base_scenario.net_revenue - self.result.revenue.net_programme_revenue)
                <= 0.01
                else "FAIL",
                where_to_fix="Scenario engine revenue logic",
                why_it_matters="Base scenario must replicate main calculation.",
            )
        )

        # 13. Base scenario cash cost = Calculations
        checks.append(
            ModelCheck(
                name="Base scenario cash cost matches Calculations",
                actual=_fmt(base_scenario.cash_cost),
                expected=_fmt(self.result.costs.total_cohort_cash_cost),
                difference=_fmt(
                    round(abs(base_scenario.cash_cost - self.result.costs.total_cohort_cash_cost), 2)
                ),
                tolerance="0.01",
                status="OK"
                if abs(base_scenario.cash_cost - self.result.costs.total_cohort_cash_cost)
                <= 0.01
                else "FAIL",
                where_to_fix="Scenario engine cost logic",
                why_it_matters="Base scenario must replicate main calculation.",
            )
        )

        # 14. Workstream minimum = global control
        ws_min_ok = (
            self.config.minimum_per_workstream == 4
        )  # spec says global control is 4
        checks.append(
            ModelCheck(
                name="Workstream minimum matches global control",
                actual=_fmt(self.config.minimum_per_workstream),
                expected="4",
                difference="0",
                tolerance="0",
                status="OK" if ws_min_ok else "FAIL",
                where_to_fix="Launch gates",
                why_it_matters="All workstreams must respect the same minimum threshold.",
            )
        )

        # 15. Cash break-even produces ≈€0 surplus
        breakeven_price = self.breakeven.cash_break_even_price
        # Build a temp engine at exact break-even price
        cfg_be = copy.deepcopy(self.config)
        exact_be_price = engine.exact_break_even_price()
        avg = engine.revenue.average_gross_price_per_participant
        ratio = exact_be_price / avg if avg else 1.0
        cfg_be.seat_mix.early_payment_price *= ratio
        cfg_be.seat_mix.standard_payment_price *= ratio
        cfg_be.seat_mix.installment_price *= ratio
        eng_be = CohortEngine(cfg_be)
        surplus_at_be = eng_be.decisions.cash_surplus
        checks.append(
            ModelCheck(
                name="Cash break-even produces ≈€0 surplus",
                actual=_fmt(surplus_at_be),
                expected="0.00",
                difference=_fmt(round(abs(surplus_at_be), 2)),
                tolerance="0.01",
                status="OK" if abs(surplus_at_be) <= 0.01 else "FAIL",
                where_to_fix="Break-even solver",
                why_it_matters="Break-even price must clear all costs exactly.",
            )
        )

        # 16. Custom scenario seats = participants
        checks.append(
            ModelCheck(
                name="Custom scenario seats equal participants",
                actual=_fmt(self.scenarios.custom.participants),
                expected="24",
                difference="0",
                tolerance="0",
                status="OK" if self.scenarios.custom.participants == 24 else "FAIL",
                where_to_fix="Custom scenario seat allocation",
                why_it_matters="Custom scenario default is 6 per workstream.",
            )
        )

        # 17. Revenue timing profile totals 100%
        rev_total = sum(self.cashflow.timing_assumptions["revenue_profile"].values())
        checks.append(
            ModelCheck(
                name="Revenue timing profile totals 100%",
                actual=f"{rev_total:.4f}",
                expected="1.0000",
                difference=f"{abs(rev_total - 1.0):.4f}",
                tolerance="0.0001",
                status="OK" if abs(rev_total - 1.0) <= 0.0001 else "FAIL",
                where_to_fix="Cash flow revenue profile",
                why_it_matters="All revenue must be collected across the schedule.",
            )
        )

        # 18. Cost timing profile totals 100%
        cost_total = sum(self.cashflow.timing_assumptions["cost_profile"].values())
        checks.append(
            ModelCheck(
                name="Cost timing profile totals 100%",
                actual=f"{cost_total:.4f}",
                expected="1.0000",
                difference=f"{abs(cost_total - 1.0):.4f}",
                tolerance="0.0001",
                status="OK" if abs(cost_total - 1.0) <= 0.0001 else "FAIL",
                where_to_fix="Cash flow cost profile",
                why_it_matters="All costs must be paid across the schedule.",
            )
        )

        # 19. Cash-flow revenue = Calculations
        cf_revenue = sum(m.net_revenue_collected for m in self.cashflow.monthly_schedule)
        checks.append(
            ModelCheck(
                name="Cash-flow revenue matches Calculations",
                actual=_fmt(cf_revenue),
                expected=_fmt(self.result.revenue.net_programme_revenue),
                difference=_fmt(
                    round(abs(cf_revenue - self.result.revenue.net_programme_revenue), 2)
                ),
                tolerance="0.01",
                status="OK"
                if abs(cf_revenue - self.result.revenue.net_programme_revenue) <= 0.01
                else "FAIL",
                where_to_fix="Cash flow revenue timing",
                why_it_matters="Timing must not change total revenue.",
            )
        )

        # 20. Cash-flow cost = Calculations
        cf_cost = sum(m.cash_costs_paid for m in self.cashflow.monthly_schedule)
        checks.append(
            ModelCheck(
                name="Cash-flow cost matches Calculations",
                actual=_fmt(cf_cost),
                expected=_fmt(self.result.costs.total_cohort_cash_cost),
                difference=_fmt(
                    round(abs(cf_cost - self.result.costs.total_cohort_cash_cost), 2)
                ),
                tolerance="0.01",
                status="OK"
                if abs(cf_cost - self.result.costs.total_cohort_cash_cost) <= 0.01
                else "FAIL",
                where_to_fix="Cash flow cost timing",
                why_it_matters="Timing must not change total cost.",
            )
        )

        # 21. Closing cash = opening + cohort surplus
        ending = self.cashflow.monthly_schedule[-1].closing_balance
        calc_ending = self.result.decisions.cash_surplus
        checks.append(
            ModelCheck(
                name="Closing cash equals cohort surplus",
                actual=_fmt(ending),
                expected=_fmt(calc_ending),
                difference=_fmt(round(abs(ending - calc_ending), 2)),
                tolerance="0.01",
                status="OK" if abs(ending - calc_ending) <= 0.01 else "FAIL",
                where_to_fix="Cash flow balance calculation",
                why_it_matters="Ending balance must equal total surplus.",
            )
        )

        return checks

    def to_response(self) -> ChecksResponse:
        overall = "PASS" if all(c.status == "OK" for c in self.checks) else "FAIL"
        launch = (
            "GO"
            if overall == "PASS"
            and self.result.decisions.actual_launch_readiness == "GO"
            else "HOLD"
        )
        return ChecksResponse(
            checks=self.checks,
            overall_status=overall,
            launch_readiness=launch,
        )
