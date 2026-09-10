"""
CareerLeap v5 Cash Flow Engine
Replicates the Excel "Cash Flow" sheet timing profiles and monthly balances.
"""

from typing import List

from backend.models import CohortConfigInput, CashFlowResponse, CashFlowMonth
from backend.engine import CohortEngine


# Timing profiles from the unified spec (must sum to 1.0)
DEFAULT_REVENUE_PROFILE = {
    "Pre-launch": 0.40,
    "Month 1": 0.25,
    "Month 2": 0.20,
    "Month 3": 0.10,
    "Extension": 0.05,
}

DEFAULT_COST_PROFILE = {
    "Pre-launch": 0.25,
    "Month 1": 0.25,
    "Month 2": 0.20,
    "Month 3": 0.20,
    "Extension": 0.10,
}


class CashFlowEngine:
    """Builds monthly cash flow schedule from a completed cohort engine."""

    def __init__(
        self,
        config: CohortConfigInput,
        engine: CohortEngine,
        revenue_profile: dict = None,
        cost_profile: dict = None,
    ):
        self.config = config
        self.engine = engine
        self.revenue_profile = revenue_profile or DEFAULT_REVENUE_PROFILE
        self.cost_profile = cost_profile or DEFAULT_COST_PROFILE
        self.monthly_schedule = self._build_schedule()

    def _build_schedule(self) -> List[CashFlowMonth]:
        net_revenue = self.engine.revenue.net_programme_revenue
        total_cost = self.engine.costs.total_cohort_cash_cost
        target_surplus = self.engine.decisions.cash_surplus

        schedule = []
        balance = 0.0
        for phase in ["Pre-launch", "Month 1", "Month 2", "Month 3", "Extension"]:
            rev_collected = round(net_revenue * self.revenue_profile[phase], 2)
            cost_paid = round(total_cost * self.cost_profile[phase], 2)
            movement = round(rev_collected - cost_paid, 2)
            opening = round(balance, 2)
            closing = round(opening + movement, 2)
            schedule.append(
                CashFlowMonth(
                    phase=phase,
                    net_revenue_collected=rev_collected,
                    cash_costs_paid=cost_paid,
                    net_cash_movement=movement,
                    opening_balance=opening,
                    closing_balance=closing,
                )
            )
            balance = closing

        # Force the final period to absorb any 1-cent rounding drift so totals
        # and the ending balance match the main calculation exactly.
        if schedule:
            sum_rev = sum(m.net_revenue_collected for m in schedule)
            sum_cost = sum(m.cash_costs_paid for m in schedule)
            delta_rev = round(net_revenue - sum_rev, 2)
            delta_cost = round(total_cost - sum_cost, 2)
            if delta_rev != 0 or delta_cost != 0:
                last = schedule[-1]
                last.net_revenue_collected = round(last.net_revenue_collected + delta_rev, 2)
                last.cash_costs_paid = round(last.cash_costs_paid + delta_cost, 2)
                last.net_cash_movement = round(
                    last.net_revenue_collected - last.cash_costs_paid, 2
                )
                # Recompute closing from the previous period's balance
                prev_closing = schedule[-2].closing_balance if len(schedule) > 1 else 0.0
                last.closing_balance = round(prev_closing + last.net_cash_movement, 2)

        return schedule

    def minimum_funding_buffer(self) -> float:
        lowest = min(m.closing_balance for m in self.monthly_schedule)
        return round(abs(lowest), 2) if lowest < 0 else 0.0

    def lowest_projected_balance(self) -> float:
        return round(min(m.closing_balance for m in self.monthly_schedule), 2)

    def ending_balance(self) -> float:
        return round(self.monthly_schedule[-1].closing_balance, 2)

    def to_response(self) -> CashFlowResponse:
        return CashFlowResponse(
            timing_assumptions={
                "revenue_profile": self.revenue_profile,
                "cost_profile": self.cost_profile,
            },
            monthly_schedule=self.monthly_schedule,
            minimum_funding_buffer=self.minimum_funding_buffer(),
            lowest_projected_balance=self.lowest_projected_balance(),
            ending_balance=self.ending_balance(),
        )
