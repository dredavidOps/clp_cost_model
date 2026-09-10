"""
Pytest fixtures for CareerLeap v5 base-case validation.
All numbers must match Section 10 of CareerLeap_Unified_Spec_v5.md to 2 decimals.
"""

import pytest

from backend.defaults import build_default_config
from backend.engine import CohortEngine
from backend.cashflow import CashFlowEngine
from backend.breakeven import BreakEvenEngine
from backend.scenarios import ScenarioEngine
from backend.sensitivity import SensitivityEngine
from backend.checks import ChecksEngine


@pytest.fixture
def base_config():
    return build_default_config()


@pytest.fixture
def base_engine(base_config):
    return CohortEngine(base_config)


def test_base_case_revenue(base_engine):
    r = base_engine.revenue
    assert round(r.participant_gross_receipts, 2) == 13764.00
    assert round(r.vat_payable, 2) == 2197.61
    assert round(r.net_programme_revenue, 2) == 11566.39
    assert round(r.average_gross_price_per_participant, 2) == 688.20


def test_base_case_costs(base_engine):
    c = base_engine.costs
    assert round(c.mentor_cost, 2) == 4480.00
    assert round(c.m365_licences, 2) == 873.60
    assert round(c.other_tools, 2) == 875.00
    assert round(c.internal_team_payments, 2) == 4200.00
    assert round(c.other_external_costs, 2) == 850.00
    assert round(c.payment_processing_fees, 2) == 344.10
    assert round(c.contingency_reserve, 2) == 1113.41
    assert round(c.total_cohort_cash_cost, 2) == 12736.11
    assert round(c.cash_cost_per_participant, 2) == 636.81


def test_base_case_decisions(base_engine):
    d = base_engine.decisions
    assert round(d.cash_surplus, 2) == -1169.72
    assert round(d.cash_surplus_margin, 4) == -0.1011
    assert round(d.cash_break_even_average_price, 2) == 760.26
    assert round(d.target_margin_average_price, 2) == 801.77
    assert d.projected_economics_status == "REVIEW"
    assert d.actual_launch_readiness == "HOLD"


def test_cash_flow_balances(base_config, base_engine):
    cf = CashFlowEngine(base_config, base_engine).to_response()
    assert round(cf.ending_balance, 2) == round(base_engine.decisions.cash_surplus, 2)
    revenue_total = sum(m.net_revenue_collected for m in cf.monthly_schedule)
    assert round(revenue_total, 2) == round(base_engine.revenue.net_programme_revenue, 2)
    cost_total = sum(m.cash_costs_paid for m in cf.monthly_schedule)
    assert round(cost_total, 2) == round(base_engine.costs.total_cohort_cash_cost, 2)


def test_break_even_curve_contains_base_price(base_engine):
    be = BreakEvenEngine(base_engine.config, base_engine, 500.0, 1000.0, 25.0)
    prices = [p.average_gross_price for p in be.curve]
    assert 500.0 in prices
    assert 1000.0 in prices
    # Break-even price from solver should fall inside the curve range
    assert 500.0 <= base_engine.decisions.cash_break_even_average_price <= 1000.0


def test_scenarios_have_four_results(base_config):
    scenarios = ScenarioEngine(base_config).generate()
    assert scenarios.conservative.name == "Conservative"
    assert scenarios.base.name == "Base"
    assert scenarios.growth.name == "Growth"
    assert scenarios.custom.name == "Custom"


def test_checks_pass_for_base_case(base_config, base_engine):
    from backend.main import calculate, scenarios, cash_flow, break_even
    result = calculate(base_config)
    scenarios_resp = scenarios(base_config)
    cf = cash_flow(base_config)
    be = break_even(base_config)
    checks = ChecksEngine(base_config, result, scenarios_resp, cf, be).to_response()
    assert checks.overall_status == "PASS"
    assert checks.launch_readiness == "HOLD"  # economics are REVIEW


def test_sensitivity_grid_shape(base_config):
    sens = SensitivityEngine(base_config).to_response()
    assert len(sens.grid) == 8  # participant_count
    assert len(sens.grid[0]) == 21  # price_count
