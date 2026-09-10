"""
CareerLeap v5 Break-Even Engine
Replicates the Excel "Break-even" sheet curve and price solver.
"""

from typing import List

from backend.models import CohortConfigInput, BreakEvenResponse, BreakEvenPoint
from backend.engine import CohortEngine


class BreakEvenEngine:
    """Generates a price-surplus curve and solves for break-even / target prices."""

    def __init__(
        self,
        config: CohortConfigInput,
        engine: CohortEngine,
        start_price: float = 500.0,
        end_price: float = 1000.0,
        step: float = 25.0,
    ):
        self.config = config
        self.engine = engine
        self.start_price = start_price
        self.end_price = end_price
        self.step = step
        self.curve = self._build_curve()

    def _surplus_at_price(self, price: float) -> tuple:
        """Return (gross, net, total_cost, surplus, margin) for a given average price."""
        participants = self.engine.total_participants()
        gross = price * participants

        if self.config.vat_applies:
            net = gross - (gross * self.config.vat_rate / (1 + self.config.vat_rate))
        else:
            net = gross

        # Scale mentor cost with participants; keep other costs fixed
        base_participants = self.engine.total_participants()
        base_mentor = self.engine.costs.mentor_cost
        mentor_ratio = participants / base_participants if base_participants else 1.0
        scaled_mentor = base_mentor * mentor_ratio

        payment_fees = gross * self.config.payment_processing_fee_rate
        external = (
            scaled_mentor
            + self.engine.costs.m365_licences
            + self.engine.costs.other_tools
            + self.engine.costs.other_external_costs
            + payment_fees
        )
        contingency = round(external * self.config.external_cost_contingency_rate, 2)
        total = external + contingency + self.engine.costs.internal_team_payments

        surplus = net - total
        margin = surplus / net if net else 0.0
        return gross, net, total, surplus, margin

    def _build_curve(self) -> List[BreakEvenPoint]:
        points = []
        price = self.start_price
        while price <= self.end_price + 1e-6:
            gross, net, total, surplus, margin = self._surplus_at_price(price)
            points.append(
                BreakEvenPoint(
                    average_gross_price=round(price, 2),
                    gross_receipts=round(gross, 2),
                    net_programme_revenue=round(net, 2),
                    total_cohort_cash_cost=round(total, 2),
                    cash_surplus=round(surplus, 2),
                    cash_surplus_margin=round(margin, 4),
                )
            )
            price += self.step
        return points

    def to_response(self) -> BreakEvenResponse:
        current = {
            "planned_participants": self.engine.total_participants(),
            "current_average_price": round(
                self.engine.revenue.average_gross_price_per_participant, 2
            ),
            "current_cash_surplus": round(self.engine.decisions.cash_surplus, 2),
            "projected_economics_status": self.engine.decisions.projected_economics_status,
        }
        return BreakEvenResponse(
            current_model=current,
            curve=self.curve,
            cash_break_even_price=round(
                self.engine.decisions.cash_break_even_average_price, 2
            ),
            target_margin_price=round(
                self.engine.decisions.target_margin_average_price, 2
            ),
            gap_current_vs_break_even=round(
                self.engine.revenue.average_gross_price_per_participant
                - self.engine.decisions.cash_break_even_average_price,
                2,
            ),
            chart_controls={
                "starting_price": self.start_price,
                "ending_price": self.end_price,
                "price_step": self.step,
            },
        )
