"""Smoke tests locking the v5.1 fixture values for the 10 business questions.

Run from the repo root:
    backend/.venv/bin/python -m pytest backend/tests/test_fixtures.py -v

Fixture notes (vs kimi_prompt_10_business_questions.md):
- Total cost €21,622.25 EXCLUDES "other" costs (mirrors the Excel model and
  AGENTS.md); other costs are tracked separately in total_costs.other.
- Break-even price computes to €553.28 (€0.01 from the prompt's €553.27,
  which truncated instead of rounding).
- Target margin price (5%) computes to €582.40 from the prompt's own closed
  form; the prompt's €801.77 figure does not reconcile with that formula.
- Pre-launch funding computes to €7,858.25 from the prompt's own timing
  profiles; the prompt's €1,170 Excel figure is not reproducible from the
  profiles given in the spec.
- "Break-even cohort size 32.2 -> 33" holds at an €688 average price, which
  requires all 40 seats priced at €688 (defaults only price 20 of 40 seats,
  so the default average price is €344.10).
"""
import copy
import os
import sys

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from backend.main import app  # noqa: E402

client = TestClient(app)


@pytest.fixture(scope="module")
def defaults():
    r = client.get("/api/config/defaults")
    assert r.status_code == 200
    return r.json()


@pytest.fixture(scope="module")
def calculated(defaults):
    r = client.post("/api/calculate", json=defaults)
    assert r.status_code == 200
    return r.json()


# ─── Q1: complete cost ───────────────────────────────────────────────────────

def test_total_cost_fixture(calculated):
    tc = calculated["total_costs"]
    assert tc["total"] == pytest.approx(21622.25, abs=0.01)
    assert tc["per_participant"] == pytest.approx(540.56, abs=0.01)
    assert len(tc["line_items"]) > 0


def test_cost_line_items_have_categories(calculated):
    cats = {item["category"] for item in calculated["total_costs"]["line_items"]}
    assert {"Tools", "Mentors", "Internal Team", "Operational"} <= cats


# ─── Q2: cost per participant ────────────────────────────────────────────────

def test_per_participant_breakdown_fixture(calculated):
    bd = calculated["total_costs"]["per_participant_breakdown"]
    assert bd["tools"] == pytest.approx(137.22, abs=0.01)
    assert bd["mentors"] == pytest.approx(120.00, abs=0.01)
    assert bd["internal_team"] == pytest.approx(269.51, abs=0.01)
    assert bd["operational"] == pytest.approx(13.83, abs=0.01)


def test_per_participant_by_workstream_present(calculated):
    by_ws = calculated["total_costs"]["per_participant_by_workstream"]
    assert set(by_ws) == {"itsa", "data", "marketing", "product"}
    # workstream-specific costs differ (marketing is the most expensive)
    assert by_ws["marketing"] > by_ws["itsa"]


def test_cost_by_workstream_reconciles(calculated):
    tc = calculated["total_costs"]
    by_ws = tc["cost_by_workstream"]
    assert set(by_ws) == {"itsa", "data", "marketing", "product"}
    # totals sum exactly to the programme total
    assert sum(by_ws.values()) == pytest.approx(tc["total"], abs=0.01)
    # equal workstream sizes -> itsa (cheapest tools) is the cheapest slice
    assert by_ws["marketing"] > by_ws["itsa"]


# ─── Q3: break-even price ────────────────────────────────────────────────────

def test_break_even_price_fixture(calculated):
    # 21622.25 / 40 / 0.977 = 553.28 (prompt fixture 553.27 within €0.01)
    assert calculated["decisions"]["cash_break_even_average_price"] == pytest.approx(553.27, abs=0.01)


# ─── Q4: target margin price ─────────────────────────────────────────────────

def test_target_margin_price_formula(calculated):
    # 21622.25 / 0.95 / 0.977 / 40 = 582.40 (closed form from the spec)
    assert calculated["decisions"]["target_margin_average_price"] == pytest.approx(582.40, abs=0.01)


# ─── Q5: break-even cohort size ──────────────────────────────────────────────

def test_break_even_cohort_size_at_688(defaults):
    cfg = copy.deepcopy(defaults)
    cfg["pricing"] = {
        "early": {"seats": 16, "price": 688},
        "standard": {"seats": 16, "price": 688},
        "installment": {"seats": 8, "price": 688},
    }
    r = client.post("/api/calculate", json=cfg)
    assert r.status_code == 200
    dec = r.json()["decisions"]
    assert dec["break_even_cohort_size"] == pytest.approx(32.2, abs=0.05)
    assert dec["minimum_viable_cohort_size"] == 33


# ─── Q6: financial outcome ───────────────────────────────────────────────────

def test_financial_outcome_fixture(calculated):
    dec = calculated["decisions"]
    assert dec["cash_surplus"] == pytest.approx(-7858.25, abs=0.01)
    assert dec["cash_surplus_margin"] == pytest.approx(-0.5709, abs=0.001)
    # pre-tax profit equals cash surplus in this model
    assert dec["pre_tax_profit"] == dec["cash_surplus"]
    rev = calculated["revenue"]
    assert rev["participant_gross_receipts"] == pytest.approx(13764.0, abs=0.01)
    assert len(rev["revenue_bridge"]) >= 3


# ─── Q7: cash flow ───────────────────────────────────────────────────────────

def test_cash_flow_funding(defaults):
    # With the spec's timing profiles the lowest closing balance is reached in
    # the Extension phase: -€7,858.25, so pre-launch funding required is €7,858.25.
    r = client.post("/api/calculate/cash-flow", json=defaults)
    assert r.status_code == 200
    cf = r.json()
    assert cf["pre_launch_funding_required"] == pytest.approx(7858.25, abs=0.01)
    assert cf["lowest_balance_amount"] < 0
    assert len(cf["monthly_schedule"]) == 5


# ─── Q9: capacity ────────────────────────────────────────────────────────────

def test_mentor_capacity_fixture(calculated):
    cap = calculated["capacity"]
    assert cap["mentor_max_capacity"] == 24  # 4 mentors x 6
    assert cap["mentor_current_demand"] == 40
    assert cap["mentor_capacity_status"] == "FAIL"


# ─── Q10: launch gates ───────────────────────────────────────────────────────

def test_launch_status_hold_at_defaults(calculated):
    assert calculated["decisions"]["launch_readiness"] == "HOLD"


def _priced_cfg(defaults, price, confirmed, secured):
    cfg = copy.deepcopy(defaults)
    cfg["pricing"] = {
        "early": {"seats": 16, "price": price},
        "standard": {"seats": 16, "price": price},
        "installment": {"seats": 8, "price": price},
    }
    cfg["launch_gates"]["confirmed_participants"] = confirmed
    cfg["launch_gates"]["secured_revenue_to_date"] = secured
    return cfg


def test_launch_status_go(defaults):
    cfg = _priced_cfg(defaults, 650, confirmed=20, secured=12000)
    r = client.post("/api/calculate", json=cfg)
    assert r.status_code == 200
    assert r.json()["decisions"]["launch_readiness"] == "GO"


def test_launch_status_review(defaults):
    # confirmed + secured gates pass, economics not VIABLE -> REVIEW
    cfg = _priced_cfg(defaults, 550, confirmed=20, secured=12000)
    r = client.post("/api/calculate", json=cfg)
    assert r.status_code == 200
    assert r.json()["decisions"]["launch_readiness"] == "REVIEW"


def test_checks_response_has_gates(defaults):
    r = client.post("/api/calculate/checks", json=defaults)
    assert r.status_code == 200
    body = r.json()
    assert set(body["launch_gates_status"]) == {
        "economics_viable", "confirmed_participants", "secured_revenue",
        "model_checks", "seat_reconciliation",
    }
    assert len(body["blocking_gates"]) > 0


# ─── API surface ─────────────────────────────────────────────────────────────

@pytest.mark.parametrize("path", [
    "/api/calculate/summary",
    "/api/calculate/break-even",
    "/api/calculate/sensitivity",
    "/api/calculate/team",
    "/api/calculate/checks",
    "/api/calculate/capacity",
    "/api/calculate/cash-flow",
])
def test_endpoints_ok(defaults, path):
    r = client.post(path, json=defaults)
    assert r.status_code == 200, r.text[:200]


def test_summary_contract(defaults):
    r = client.post("/api/calculate/summary", json=defaults)
    assert r.status_code == 200
    s = r.json()
    assert s["total_participants"] == 40
    assert s["total_cost"] == pytest.approx(21622.25, abs=0.01)
    assert s["break_even_price"] == pytest.approx(553.27, abs=0.01)
    assert s["launch_status"] == "HOLD"


def test_scenario_compare(defaults):
    r = client.post("/api/scenarios/compare", json={
        "scenarios": [defaults, defaults],
        "names": ["A", "B"],
    })
    assert r.status_code == 200
    comps = r.json()["comparisons"]
    assert len(comps) == 2
    assert comps[0]["name"] == "A"
    assert comps[0]["total_cost"] == pytest.approx(21622.25, abs=0.01)


def test_export_csv(defaults):
    r = client.post("/api/export/csv", json=defaults)
    assert r.status_code == 200
    assert "total_programme_cost" in r.text
