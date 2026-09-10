"""backend/main.py — FastAPI routes for CareerLeap Pricing Dashboard v5.1."""
import csv
import io
from typing import Any, Dict, List

from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware

from .models import (
    PricingScenarioInput,
    FullCalculateResponse,
    SummaryResponse,
    BreakEvenResponse,
    SensitivityResponse,
    TeamResponse,
    ChecksResponse,
    CapacityResult,
    CashFlowResult,
    ScenarioCompareRequest,
    ScenarioCompareResponse,
)
from . import engine, validators

app = FastAPI(title="CareerLeap Pricing Dashboard API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _run_checks(config: PricingScenarioInput) -> ChecksResponse:
    revenue = engine.calculate_revenue(config)
    total_cost = engine.calculate_total_cost(config, revenue.net_programme_revenue)
    decisions = engine.calculate_decisions(config, revenue, total_cost)
    return validators.run_checks(
        config, decisions.dict(), total_cost.dict(), revenue.dict()
    )


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/config/defaults", response_model=PricingScenarioInput)
def defaults():
    return PricingScenarioInput()


@app.post("/api/calculate", response_model=FullCalculateResponse)
def calculate(config: PricingScenarioInput):
    result = engine.run_full_calculation(config)
    # validators factor in model-check failures on top of the engine's gates
    checks = validators.run_checks(
        config,
        result["decisions"].dict(),
        result["total_costs"].dict(),
        result["revenue"].dict(),
    )
    result["decisions"].launch_readiness = checks.launch_readiness
    return result


@app.post("/api/calculate/summary", response_model=SummaryResponse)
def summary(config: PricingScenarioInput):
    revenue = engine.calculate_revenue(config)
    total_cost = engine.calculate_total_cost(config, revenue.net_programme_revenue)
    decisions = engine.calculate_decisions(config, revenue, total_cost)
    checks = validators.run_checks(config, decisions.dict(), total_cost.dict(), revenue.dict())
    total_participants = sum(config.workstreams.dict().values())
    return SummaryResponse(
        total_participants=total_participants,
        total_revenue=revenue.net_programme_revenue,
        total_cost=total_cost.total,
        net_margin=decisions.cash_surplus,
        margin_pct=decisions.cash_surplus_margin,
        cost_per_participant=total_cost.per_participant,
        profit_per_participant=engine._r(decisions.cash_surplus / total_participants) if total_participants > 0 else 0.0,
        break_even_price=decisions.cash_break_even_average_price,
        break_even_cohort_size=decisions.break_even_cohort_size,
        target_margin_price=decisions.target_margin_average_price,
        launch_status=checks.launch_readiness,
    )


@app.post("/api/calculate/break-even", response_model=BreakEvenResponse)
def break_even(config: PricingScenarioInput):
    revenue = engine.calculate_revenue(config)
    total_cost = engine.calculate_total_cost(config, revenue.net_programme_revenue)
    decisions = engine.calculate_decisions(config, revenue, total_cost)
    curve = engine.calculate_break_even_curve(config, total_cost)
    return BreakEvenResponse(
        current_model={
            "total_participants": sum(config.workstreams.dict().values()),
            "average_gross_price": revenue.average_gross_price,
            "total_cost": total_cost.total,
            "cash_surplus": decisions.cash_surplus,
            "cash_surplus_margin": decisions.cash_surplus_margin,
        },
        curve=curve,
        cash_break_even_price=decisions.cash_break_even_average_price,
        target_margin_price=decisions.target_margin_average_price,
        gap_current_vs_break_even=engine._r(
            revenue.average_gross_price - decisions.cash_break_even_average_price
        ),
    )


@app.post("/api/calculate/sensitivity", response_model=SensitivityResponse)
def sensitivity(config: PricingScenarioInput):
    revenue = engine.calculate_revenue(config)
    total_cost = engine.calculate_total_cost(config, revenue.net_programme_revenue)
    grid = engine.calculate_sensitivity(config, total_cost)

    # Analytic break-even price per cohort size in the grid
    break_even_prices: List[Dict[str, Any]] = []
    fee = config.assumptions.payment_processing_fee_rate
    vat_applies = config.assumptions.vat_treatment == "taxable"
    vat = config.assumptions.vat_rate
    planned = sum(config.workstreams.dict().values())
    for row in grid:
        participants = row[0].participants
        scaled = total_cost.total * (participants / planned) if planned > 0 else total_cost.total
        bep = scaled / participants / (1 - fee) if participants > 0 and fee < 1 else 0.0
        if vat_applies:
            bep = bep / (1 + vat)
        break_even_prices.append({
            "participants": participants,
            "break_even_price": engine._r(bep),
        })

    return SensitivityResponse(
        current_reference={
            "participants": sum(config.workstreams.dict().values()),
            "average_gross_price": revenue.average_gross_price,
            "total_cost": total_cost.total,
            "cash_surplus": revenue.net_programme_revenue - total_cost.total,
        },
        grid=grid,
        break_even_prices=break_even_prices,
        controls={
            "price_axis": {"min": 500, "max": 1000, "step": 25},
            "cohort_axis": {"min": 12, "max": 50, "step": 4},
        },
    )


@app.post("/api/calculate/team", response_model=TeamResponse)
def team(config: PricingScenarioInput):
    return engine.calculate_team_compensation(config)


@app.post("/api/calculate/checks", response_model=ChecksResponse)
def checks(config: PricingScenarioInput):
    return _run_checks(config)


@app.post("/api/calculate/capacity", response_model=CapacityResult)
def capacity(config: PricingScenarioInput):
    return engine.calculate_capacity(config)


@app.post("/api/calculate/cash-flow", response_model=CashFlowResult)
def cash_flow(config: PricingScenarioInput):
    revenue = engine.calculate_revenue(config)
    total_cost = engine.calculate_total_cost(config, revenue.net_programme_revenue)
    return engine.calculate_cash_flow(config, revenue, total_cost)


@app.post("/api/scenarios/compare", response_model=ScenarioCompareResponse)
def compare_scenarios(payload: ScenarioCompareRequest):
    if not payload.scenarios:
        raise HTTPException(status_code=422, detail="At least one scenario is required")
    if len(payload.scenarios) > 5:
        raise HTTPException(status_code=422, detail="At most 5 scenarios can be compared")
    comparisons = engine.compare_scenarios(payload.scenarios, payload.names)
    return ScenarioCompareResponse(comparisons=comparisons)


@app.post("/api/export/csv")
def export_csv(config: PricingScenarioInput):
    revenue = engine.calculate_revenue(config)
    tools = engine.calculate_tools(config)
    mentors = engine.calculate_mentors(config)
    internal_team = engine.calculate_internal_team(config)
    operational = engine.calculate_operational(config)
    other = engine.calculate_other_costs(config, revenue.net_programme_revenue)
    total_cost = engine.calculate_total_cost(config, revenue.net_programme_revenue)
    decisions = engine.calculate_decisions(config, revenue, total_cost)
    checks = validators.run_checks(config, decisions.dict(), total_cost.dict(), revenue.dict())
    cash_flow = engine.calculate_cash_flow(config, revenue, total_cost)
    capacity = engine.calculate_capacity(config)

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow(["section", "key", "value"])

    for key, value in config.assumptions.dict().items():
        writer.writerow(["assumptions", key, value])

    for ws in engine.WORKSTREAM_ORDER:
        writer.writerow(["workstreams", "{}_participants".format(ws), getattr(config.workstreams, ws)])

    for ws in engine.WORKSTREAM_ORDER:
        for tool_key, value in getattr(config.tools, ws).dict().items():
            writer.writerow(["tools", "{}_{}".format(ws, tool_key), value])

    for key, value in config.internal_team.dict().items():
        if isinstance(value, dict):
            for sub, subval in value.items():
                writer.writerow(["internal_team", "{}_{}".format(key, sub), subval])
        else:
            writer.writerow(["internal_team", key, value])

    for key, value in config.operational.dict().items():
        if isinstance(value, dict):
            for sub, subval in value.items():
                writer.writerow(["operational", "{}_{}".format(key, sub), subval])
        else:
            writer.writerow(["operational", key, value])

    for key, value in config.other_costs.dict().items():
        if isinstance(value, dict):
            for sub, subval in value.items():
                writer.writerow(["other_costs", "{}_{}".format(key, sub), subval])
        else:
            writer.writerow(["other_costs", key, value])

    for tier in ["early", "standard", "installment"]:
        tier_spec = getattr(config.pricing, tier)
        writer.writerow(["pricing", "{}_seats".format(tier), tier_spec.seats])
        writer.writerow(["pricing", "{}_price".format(tier), tier_spec.price])

    for key, value in config.launch_gates.dict().items():
        writer.writerow(["launch_gates", key, value])

    writer.writerow(["outputs", "total_participants", sum(config.workstreams.dict().values())])
    writer.writerow(["outputs", "participant_gross_receipts", revenue.participant_gross_receipts])
    writer.writerow(["outputs", "vat_payable", revenue.vat_payable])
    writer.writerow(["outputs", "net_programme_revenue", revenue.net_programme_revenue])
    writer.writerow(["outputs", "average_gross_price", revenue.average_gross_price])
    writer.writerow(["outputs", "average_net_price", revenue.average_net_price])
    writer.writerow(["outputs", "immediate_receipts", revenue.immediate_receipts])
    writer.writerow(["outputs", "deferred_receipts", revenue.deferred_receipts])
    writer.writerow(["outputs", "total_tools_usd", tools.total_tools_usd])
    writer.writerow(["outputs", "total_tools_eur", tools.total_tools_eur])
    writer.writerow(["outputs", "mentor_total", mentors.total])
    writer.writerow(["outputs", "internal_team_total", internal_team.total])
    writer.writerow(["outputs", "operational_total", operational.total])
    writer.writerow(["outputs", "other_costs_total", other.total])
    writer.writerow(["outputs", "total_programme_cost", total_cost.total])
    writer.writerow(["outputs", "cost_per_participant", total_cost.per_participant])
    writer.writerow(["outputs", "cash_surplus", decisions.cash_surplus])
    writer.writerow(["outputs", "cash_surplus_margin", decisions.cash_surplus_margin])
    writer.writerow(["outputs", "cash_break_even_price", decisions.cash_break_even_average_price])
    writer.writerow(["outputs", "target_margin_price", decisions.target_margin_average_price])
    writer.writerow(["outputs", "price_gap_to_target", decisions.price_gap_to_target])
    writer.writerow(["outputs", "break_even_cohort_size", decisions.break_even_cohort_size])
    writer.writerow(["outputs", "minimum_viable_cohort_size", decisions.minimum_viable_cohort_size])
    writer.writerow(["outputs", "pre_tax_profit", decisions.pre_tax_profit])
    writer.writerow(["outputs", "economics_status", decisions.economics_status])
    writer.writerow(["outputs", "launch_readiness", checks.launch_readiness])
    writer.writerow(["outputs", "overall_checks_status", checks.overall_status])

    for month in cash_flow.monthly_schedule:
        writer.writerow([
            "cash_flow",
            month.phase,
            "in={} out={} closing={}".format(month.net_revenue_collected, month.cash_costs_paid, month.closing_balance),
        ])
    writer.writerow(["cash_flow", "pre_launch_funding_required", cash_flow.pre_launch_funding_required])

    writer.writerow(["capacity", "mentor_status", capacity.mentor_capacity_status])
    writer.writerow(["capacity", "tool_status", capacity.tool_limit_status])
    writer.writerow(["capacity", "team_status", capacity.team_bandwidth_status])

    filename = "careerleap_pricing_scenario.csv"
    headers = {"Content-Disposition": "attachment; filename={}".format(filename)}
    return Response(content=output.getvalue(), media_type="text/csv", headers=headers)
