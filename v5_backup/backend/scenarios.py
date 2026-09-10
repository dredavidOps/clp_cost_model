"""
CareerLeap v5 Scenario Engine
Replicates the Excel "Scenarios" sheet (Conservative / Base / Growth / Custom).
"""

import copy
import math

from backend.models import CohortConfigInput, ScenariosResponse, ScenarioResult
from backend.engine import CohortEngine


class ScenarioEngine:
    """Generates the four standard scenarios from a base config."""

    def __init__(self, config: CohortConfigInput):
        self.base_config = config

    def _make_config(
        self,
        participants_per_stream: int,
        price_multiplier: float,
        workload_multiplier: float,
        extension_weeks: int,
    ) -> CohortConfigInput:
        cfg = copy.deepcopy(self.base_config)

        cfg.workstreams.it_systems_admin = participants_per_stream
        cfg.workstreams.data_bi_ai = participants_per_stream
        cfg.workstreams.product_project_ops = participants_per_stream
        cfg.workstreams.digital_marketing_growth = participants_per_stream

        cfg.extension_wrapup_weeks = extension_weeks
        cfg.internal_team_workload_multiplier = workload_multiplier

        sm = cfg.seat_mix
        total = participants_per_stream * 4
        # Keep same seat proportions unless they don't divide evenly
        base_total = (
            sm.early_payment_seats + sm.standard_payment_seats + sm.installment_seats
        )
        if base_total == 0:
            ratio = 0
        else:
            ratio = total / base_total

        sm.early_payment_seats = max(0, math.floor(sm.early_payment_seats * ratio))
        sm.standard_payment_seats = max(
            0, math.floor(sm.standard_payment_seats * ratio)
        )
        sm.installment_seats = max(
            0, total - sm.early_payment_seats - sm.standard_payment_seats
        )

        sm.early_payment_price = round(sm.early_payment_price * price_multiplier, 2)
        sm.standard_payment_price = round(
            sm.standard_payment_price * price_multiplier, 2
        )
        sm.installment_price = round(sm.installment_price * price_multiplier, 2)

        return cfg

    def _run_scenario(
        self,
        name: str,
        participants_per_stream: int,
        price_multiplier: float,
        workload_multiplier: float,
        extension_weeks: int,
    ) -> ScenarioResult:
        cfg = self._make_config(
            participants_per_stream, price_multiplier, workload_multiplier, extension_weeks
        )
        eng = CohortEngine(cfg)

        return ScenarioResult(
            name=name,
            participants=eng.total_participants(),
            net_revenue=round(eng.revenue.net_programme_revenue, 2),
            cash_cost=round(eng.costs.total_cohort_cash_cost, 2),
            cash_surplus=round(eng.decisions.cash_surplus, 2),
            cash_surplus_margin=round(eng.decisions.cash_surplus_margin, 4),
            cash_cost_per_participant=round(eng.costs.cash_cost_per_participant, 2),
            average_gross_price=round(
                eng.revenue.average_gross_price_per_participant, 2
            ),
            target_margin_price=round(
                eng.decisions.target_margin_average_price, 2
            ),
            price_gap_to_target=round(eng.decisions.price_gap_to_target, 2),
            status=eng.decisions.projected_economics_status,
        )

    def generate(self) -> ScenariosResponse:
        # Defaults from spec Section 5.4
        conservative = self._run_scenario(
            "Conservative", 4, 0.95, 1.0, 1
        )
        base = self._run_scenario("Base", 5, 1.00, 1.0, 1)
        growth = self._run_scenario("Growth", 10, 1.05, 2.0, 2)
        custom = self._run_scenario("Custom", 6, 1.10, 1.0, 1)

        return ScenariosResponse(
            conservative=conservative,
            base=base,
            growth=growth,
            custom=custom,
        )
