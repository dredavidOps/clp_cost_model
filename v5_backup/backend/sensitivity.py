"""
CareerLeap v5 Sensitivity Engine
Two-variable decision table: average price × cohort size.
"""

import copy
from typing import List

from backend.models import CohortConfigInput, SensitivityResponse, SensitivityCell
from backend.engine import CohortEngine


class SensitivityEngine:
    """Generate a price × participants heatmap and break-even price column."""

    def __init__(
        self,
        config: CohortConfigInput,
        start_price: float = 500.0,
        price_step: float = 25.0,
        start_participants: int = 12,
        participant_step: int = 4,
        price_count: int = 21,
        participant_count: int = 8,
    ):
        self.config = config
        self.start_price = start_price
        self.price_step = price_step
        self.start_participants = start_participants
        self.participant_step = participant_step
        self.price_count = price_count
        self.participant_count = participant_count
        self.grid = self._build_grid()

    def _run_cell(self, participants: int, avg_price: float) -> SensitivityCell:
        # Make a temporary config with this price and participant count
        import copy

        cfg = copy.deepcopy(self.config)
        # Distribute participants evenly across workstreams
        per_stream = participants // 4
        remainder = participants % 4
        cfg.workstreams.it_systems_admin = per_stream + (1 if remainder > 0 else 0)
        cfg.workstreams.data_bi_ai = per_stream + (1 if remainder > 1 else 0)
        cfg.workstreams.product_project_ops = per_stream + (1 if remainder > 2 else 0)
        cfg.workstreams.digital_marketing_growth = per_stream

        # Scale seat mix prices to new average, keeping relative proportions
        base_avg = (
            self.config.seat_mix.early_payment_price
            + self.config.seat_mix.standard_payment_price
            + self.config.seat_mix.installment_price
        ) / 3
        ratio = avg_price / base_avg if base_avg else 1.0
        cfg.seat_mix.early_payment_price *= ratio
        cfg.seat_mix.standard_payment_price *= ratio
        cfg.seat_mix.installment_price *= ratio

        # Adjust seat counts proportionally to participants
        base_total = (
            self.config.seat_mix.early_payment_seats
            + self.config.seat_mix.standard_payment_seats
            + self.config.seat_mix.installment_seats
        )
        if base_total > 0:
            ratio_seats = participants / base_total
            cfg.seat_mix.early_payment_seats = max(
                0, round(cfg.seat_mix.early_payment_seats * ratio_seats)
            )
            cfg.seat_mix.standard_payment_seats = max(
                0, round(cfg.seat_mix.standard_payment_seats * ratio_seats)
            )
            cfg.seat_mix.installment_seats = max(
                0, participants - cfg.seat_mix.early_payment_seats - cfg.seat_mix.standard_payment_seats
            )

        eng = CohortEngine(cfg)
        surplus = eng.decisions.cash_surplus
        return SensitivityCell(
            participants=participants,
            average_price=round(avg_price, 2),
            cash_surplus=round(surplus, 2),
            cash_surplus_margin=round(eng.decisions.cash_surplus_margin, 4),
            status="surplus" if surplus >= 0 else "deficit",
        )

    def _build_grid(self) -> List[List[SensitivityCell]]:
        grid = []
        for p_idx in range(self.participant_count):
            participants = self.start_participants + p_idx * self.participant_step
            row = []
            for pr_idx in range(self.price_count):
                price = self.start_price + pr_idx * self.price_step
                row.append(self._run_cell(participants, price))
            grid.append(row)
        return grid

    def _break_even_for_participants(self, participants: int) -> float:
        cfg = copy.deepcopy(self.config)
        per_stream = participants // 4
        remainder = participants % 4
        cfg.workstreams.it_systems_admin = per_stream + (1 if remainder > 0 else 0)
        cfg.workstreams.data_bi_ai = per_stream + (1 if remainder > 1 else 0)
        cfg.workstreams.product_project_ops = per_stream + (1 if remainder > 2 else 0)
        cfg.workstreams.digital_marketing_growth = per_stream
        eng = CohortEngine(cfg)
        return round(eng.decisions.cash_break_even_average_price, 2)

    def break_even_prices(self) -> List[dict]:
        return [
            {
                "participants": self.start_participants + i * self.participant_step,
                "break_even_price": self._break_even_for_participants(
                    self.start_participants + i * self.participant_step
                ),
            }
            for i in range(self.participant_count)
        ]

    def to_response(self) -> SensitivityResponse:
        base_engine = CohortEngine(self.config)
        return SensitivityResponse(
            current_reference={
                "participants": base_engine.total_participants(),
                "average_price": round(
                    base_engine.revenue.average_gross_price_per_participant, 2
                ),
                "cash_surplus": round(base_engine.decisions.cash_surplus, 2),
            },
            grid=self.grid,
            break_even_prices=self.break_even_prices(),
            controls={
                "starting_price": self.start_price,
                "price_step": self.price_step,
                "starting_participants": self.start_participants,
                "participant_step": self.participant_step,
            },
        )
