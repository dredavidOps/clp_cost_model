#!/usr/bin/env python3
"""
CareerLeap Business Model Engine
================================
A production-grade cohort economics calculator for CareerLeap Academy.

Features:
  - Interactive scenario modeling (participant fee, cohort size, stipends, overhead)
  - Multi-cohort annual projections
  - Sensitivity analysis (what-if on key variables)
  - Pricing tier recommendations
  - Break-even and runway calculations
  - Export to CSV for spreadsheet analysis

Usage:
    python careerleap_business_engine.py

Or import as a module:
    from careerleap_business_engine import CohortModel, AnnualProjection
"""

from dataclasses import dataclass, field
from typing import List, Dict, Tuple
import csv
import json
from datetime import datetime


# ─── DATA MODELS ────────────────────────────────────────────────────────────

@dataclass
class CohortConfig:
    """Input parameters for a single cohort."""
    participant_fee: float = 1200.0
    cohort_size: int = 15
    duration_months: int = 4
    num_leads: int = 3
    stipend_per_lead: float = 3000.0
    overhead_per_participant: float = 150.0
    tool_cost_per_user_per_month: float = 12.0
    fixed_tool_cost_per_month: float = 42.0
    placement_bonus_per_lead: float = 0.0
    no_show_rate: float = 0.05
    refund_rate: float = 0.03


@dataclass
class CohortResult:
    """Output metrics for a single cohort."""
    revenue: float = 0.0
    tool_costs: float = 0.0
    overhead: float = 0.0
    lead_costs: float = 0.0
    placement_bonuses: float = 0.0
    total_costs: float = 0.0
    net_margin: float = 0.0
    margin_pct: float = 0.0
    cost_per_participant: float = 0.0
    profit_per_participant: float = 0.0
    break_even_size: float = 0.0
    effective_lead_hourly: float = 0.0


@dataclass
class PricingTier:
    """A recommended pricing tier."""
    name: str
    fee: float
    description: str
    projected_margin: float = 0.0
    projected_margin_pct: float = 0.0


# ─── CORE ENGINE ────────────────────────────────────────────────────────────

class CohortModel:
    """Calculates economics for a single cohort."""

    HOURS_PER_LEAD = 50  # Estimated hours per lead over a cohort

    def __init__(self, config: CohortConfig):
        self.config = config
        self.result = self._calculate()

    def _calculate(self) -> CohortResult:
        cfg = self.config
        r = CohortResult()

        # Revenue (accounting for no-shows and refunds)
        effective_participants = cfg.cohort_size * (1 - cfg.no_show_rate - cfg.refund_rate)
        r.revenue = cfg.participant_fee * effective_participants

        # Costs
        r.tool_costs = (
            cfg.tool_cost_per_user_per_month * cfg.cohort_size * cfg.duration_months
            + cfg.fixed_tool_cost_per_month * cfg.duration_months
        )
        r.overhead = cfg.overhead_per_participant * cfg.cohort_size
        r.lead_costs = cfg.stipend_per_lead * cfg.num_leads
        r.placement_bonuses = cfg.placement_bonus_per_lead * cfg.num_leads
        r.total_costs = r.tool_costs + r.overhead + r.lead_costs + r.placement_bonuses

        # Margins
        r.net_margin = r.revenue - r.total_costs
        r.margin_pct = (r.net_margin / r.revenue * 100) if r.revenue > 0 else 0
        r.cost_per_participant = r.total_costs / cfg.cohort_size
        r.profit_per_participant = r.net_margin / cfg.cohort_size
        r.break_even_size = r.total_costs / cfg.participant_fee
        r.effective_lead_hourly = cfg.stipend_per_lead / self.HOURS_PER_LEAD

        return r

    def get_pricing_tiers(self) -> List[PricingTier]:
        """Generate recommended pricing tiers based on cost structure."""
        cost_per = self.result.cost_per_participant
        tiers = [
            PricingTier("Budget / pilot", cost_per * 1.3, "Low margin, high volume, testing phase"),
            PricingTier("Standard", cost_per * 1.8, "Healthy margin, accessible price point"),
            PricingTier("Premium", cost_per * 2.2, "Strong margin, selective intake"),
            PricingTier("B2B / University", cost_per * 2.8, "White-label partner pricing"),
        ]
        for t in tiers:
            projected_revenue = t.fee * self.config.cohort_size
            t.projected_margin = projected_revenue - self.result.total_costs
            t.projected_margin_pct = (t.projected_margin / projected_revenue * 100) if projected_revenue > 0 else 0
        return tiers

    def sensitivity(self, variable: str, range_pct: List[float]) -> List[Tuple[float, float]]:
        """
        Run sensitivity analysis on a variable.
        Returns list of (adjusted_value, margin_pct).
        """
        base = getattr(self.config, variable)
        results = []
        for pct in range_pct:
            adjusted = base * (1 + pct)
            temp_config = CohortConfig(**{**self.config.__dict__, variable: adjusted})
            temp_model = CohortModel(temp_config)
            results.append((adjusted, temp_model.result.margin_pct))
        return results

    def print_report(self):
        """Print a formatted report to console."""
        cfg = self.config
        res = self.result

        print("=" * 64)
        print("CAREERLEAP COHORT ECONOMICS REPORT".center(64))
        print("=" * 64)

        print(f"ASSUMPTIONS")
        print(f"  {'─' * 60}")
        print(f"  Participant fee:          {self._fmt(cfg.participant_fee)}")
        print(f"  Cohort size:              {cfg.cohort_size}")
        print(f"  Duration:                 {cfg.duration_months} months")
        print(f"  Team leads:               {cfg.num_leads}")
        print(f"  Stipend per lead:         {self._fmt(cfg.stipend_per_lead)}")
        print(f"  Overhead / participant:   {self._fmt(cfg.overhead_per_participant)}")
        print(f"  Tool cost / user / mo:    {self._fmt(cfg.tool_cost_per_user_per_month)}")
        print(f"  Fixed tool cost / mo:     {self._fmt(cfg.fixed_tool_cost_per_month)}")
        print(f"  No-show rate:             {cfg.no_show_rate * 100:.0f}%")
        print(f"  Refund rate:              {cfg.refund_rate * 100:.0f}%")

        print(f"REVENUE & COSTS")
        print(f"  {'─' * 60}")
        print(f"  Total revenue:            {self._fmt(res.revenue)}")
        print(f"  Tool costs:               {self._fmt(res.tool_costs)}")
        print(f"  Overhead:                 {self._fmt(res.overhead)}")
        print(f"  Lead costs:               {self._fmt(res.lead_costs)}")
        print(f"  Placement bonuses:        {self._fmt(res.placement_bonuses)}")
        print(f"  {'─' * 60}")
        print(f"  TOTAL COSTS:              {self._fmt(res.total_costs)}")

        print(f"MARGIN & HEALTH")
        print(f"  {'─' * 60}")
        margin_status = "✓ Healthy" if res.margin_pct >= 30 else "⚠ Tight" if res.margin_pct >= 15 else "✗ At risk"
        print(f"  Net margin:               {self._fmt(res.net_margin)}  ({res.margin_pct:.1f}%)  {margin_status}")
        print(f"  Cost per participant:     {self._fmt(res.cost_per_participant)}")
        print(f"  Profit per participant:   {self._fmt(res.profit_per_participant)}")
        print(f"  Break-even cohort size:   {res.break_even_size:.1f} participants")
        print(f"  Effective lead hourly:    €{res.effective_lead_hourly:.0f}/hr")

        print(f"RECOMMENDED PRICING TIERS")
        print(f"  {'─' * 60}")
        print(f"  {'Tier':<22} {'Fee':<12} {'Margin':<16} {'Status'}")
        for t in self.get_pricing_tiers():
            status = "✓" if t.projected_margin_pct >= 30 else "⚠" if t.projected_margin_pct >= 15 else "✗"
            print(f"  {t.name:<22} {self._fmt(t.fee):<12} {self._fmt(t.projected_margin)} ({t.projected_margin_pct:.0f}%)  {status}")

        print(f"SENSITIVITY: PARTICIPANT FEE")
        print(f"  {'─' * 60}")
        print(f"  {'Fee':<14} {'Margin %':<12} {'Status'}")
        for fee, mp in self.sensitivity("participant_fee", [-0.2, -0.1, 0, 0.1, 0.2, 0.5, 1.0]):
            status = "✓" if mp >= 30 else "⚠" if mp >= 15 else "✗"
            print(f"  {self._fmt(fee):<14} {mp:>6.1f}%       {status}")

        print(f"SENSITIVITY: COHORT SIZE")
        print(f"  {'─' * 60}")
        print(f"  {'Size':<10} {'Revenue':<14} {'Margin':<14} {'Margin %':<10}")
        for size, mp in self.sensitivity("cohort_size", [-0.33, -0.2, -0.1, 0, 0.1, 0.33, 1.0]):
            rev = size * cfg.participant_fee
            mar = rev - res.total_costs
            print(f"  {int(size):<10} {self._fmt(rev):<14} {self._fmt(mar):<14} {mp:>6.1f}%")

        print("" + "=" * 64)

    @staticmethod
    def _fmt(val: float) -> str:
        return f"€{val:,.0f}"


class AnnualProjection:
    """Projects multiple cohorts over a year."""

    def __init__(self, cohort_config: CohortConfig, cohorts_per_year: int = 4):
        self.config = cohort_config
        self.cohorts_per_year = cohorts_per_year
        self.cohort_model = CohortModel(cohort_config)

    def project(self) -> Dict:
        """Return annual projection summary."""
        r = self.cohort_model.result
        return {
            "cohorts_per_year": self.cohorts_per_year,
            "total_participants": self.config.cohort_size * self.cohorts_per_year,
            "annual_revenue": r.revenue * self.cohorts_per_year,
            "annual_costs": r.total_costs * self.cohorts_per_year,
            "annual_margin": r.net_margin * self.cohorts_per_year,
            "annual_margin_pct": r.margin_pct,
            "total_lead_costs": r.lead_costs * self.cohorts_per_year,
            "total_tool_costs": r.tool_costs * self.cohorts_per_year,
        }

    def print_projection(self):
        p = self.project()
        print("" + "=" * 64)
        print("ANNUAL PROJECTION".center(64))
        print("=" * 64)
        print(f"  Cohorts per year:         {p['cohorts_per_year']}")
        print(f"  Total participants:       {p['total_participants']}")
        print(f"  Annual revenue:           €{p['annual_revenue']:,.0f}")
        print(f"  Annual costs:             €{p['annual_costs']:,.0f}")
        print(f"  Annual margin:            €{p['annual_margin']:,.0f}  ({p['annual_margin_pct']:.1f}%)")
        print(f"  Total lead costs:         €{p['total_lead_costs']:,.0f}")
        print(f"  Total tool costs:         €{p['total_tool_costs']:,.0f}")
        print("=" * 64)


# ─── EXPORT UTILITIES ───────────────────────────────────────────────────────

def export_scenarios_to_csv(filename: str = "careerleap_scenarios.csv"):
    """Export a grid of scenarios (fee × cohort size) to CSV."""
    fees = [800, 1000, 1200, 1500, 1800, 2200, 2500]
    sizes = [8, 10, 12, 15, 18, 20, 25]

    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
            'participant_fee', 'cohort_size', 'revenue', 'total_costs',
            'net_margin', 'margin_pct', 'cost_per_participant', 'break_even_size'
        ])

        for fee in fees:
            for size in sizes:
                cfg = CohortConfig(participant_fee=fee, cohort_size=size)
                model = CohortModel(cfg)
                res = model.result
                writer.writerow([
                    fee, size,
                    round(res.revenue), round(res.total_costs),
                    round(res.net_margin), round(res.margin_pct, 1),
                    round(res.cost_per_participant, 2), round(res.break_even_size, 1)
                ])

    print(f"✓ Exported {len(fees) * len(sizes)} scenarios to {filename}")


# ─── INTERACTIVE CLI ────────────────────────────────────────────────────────

def interactive():
    """Run the interactive business engine."""
    print("\n" + "╔" + "═" * 62 + "╗")
    print("║" + "  CAREERLEAP BUSINESS MODEL ENGINE".center(62) + "║")
    print("║" + "  Cohort economics, pricing & projections".center(62) + "║")
    print("╚" + "═" * 62 + "╝")

    print("\n  Default configuration loaded. Press Enter to accept defaults.\n")

    def ask(prompt: str, default, type_fn=float):
        val = input(f"  {prompt} [{default}]: ").strip()
        return type_fn(val) if val else default

    cfg = CohortConfig(
        participant_fee=ask("Participant fee (€)", 1200),
        cohort_size=ask("Cohort size", 15, int),
        duration_months=ask("Duration (months)", 4, int),
        num_leads=ask("Team leads", 3, int),
        stipend_per_lead=ask("Stipend per lead (€)", 3000),
        overhead_per_participant=ask("Overhead / participant (€)", 150),
        tool_cost_per_user_per_month=ask("Tool cost / user / month (€)", 12),
        fixed_tool_cost_per_month=ask("Fixed tool cost / month (€)", 42),
        placement_bonus_per_lead=ask("Placement bonus / lead (€)", 0),
        no_show_rate=ask("No-show rate (%)", 5) / 100,
        refund_rate=ask("Refund rate (%)", 3) / 100,
    )

    model = CohortModel(cfg)
    model.print_report()

    # Annual projection
    cohorts = ask("\n  Cohorts per year", 4, int)
    annual = AnnualProjection(cfg, cohorts)
    annual.print_projection()

    # Export option
    if input("\n  Export scenario grid to CSV? (y/n) [n]: ").strip().lower() == 'y':
        export_scenarios_to_csv()

    print("\n  Done!\n")


if __name__ == "__main__":
    interactive()