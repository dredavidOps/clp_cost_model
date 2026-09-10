from typing import List

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from backend.models import (
    CohortConfigInput,
    OtherExternalCost,
    CalculateResponse,
    ScenariosResponse,
    SensitivityResponse,
    CashFlowResponse,
    BreakEvenResponse,
    ChecksResponse,
    ToolBreakdownItem,
    CareerTrackOutput,
    TeamRoster,
    PricingTierDefaults,
)
from backend.engine import CohortEngine
from backend.cashflow import CashFlowEngine
from backend.breakeven import BreakEvenEngine
from backend.scenarios import ScenarioEngine
from backend.sensitivity import SensitivityEngine
from backend.checks import ChecksEngine
from backend.career_tracks import CAREER_TRACKS, get_tool_cost_per_user
from backend.defaults import (
    build_default_config,
    load_team_roster,
    load_pricing_tiers,
    load_tools_registry,
)

app = FastAPI(title="CareerLeap Business Model API v5")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/defaults", response_model=CohortConfigInput)
def defaults():
    return build_default_config()


@app.get("/api/team-roster", response_model=TeamRoster)
def team_roster():
    return TeamRoster(members=load_team_roster())


@app.get("/api/pricing-tiers", response_model=PricingTierDefaults)
def pricing_tiers():
    return PricingTierDefaults(seat_mix=load_pricing_tiers()["seat_mix"])


@app.get("/api/career-tracks", response_model=List[CareerTrackOutput])
def career_tracks():
    return [
        CareerTrackOutput(
            key=key,
            label=track["label"],
            short_name=track["short_name"],
            role_in_simulation=track["role_in_simulation"],
            skills=track["skills"],
            tools=[ToolBreakdownItem(**tool) for tool in track["tools"]],
            track_total_tool_cost=track["track_total_tool_cost"],
            track_cost_per_participant=track["track_cost_per_participant"],
            total_tool_cost_per_user_per_month=get_tool_cost_per_user(key),
        )
        for key, track in CAREER_TRACKS.items()
    ]


@app.post("/api/calculate", response_model=CalculateResponse)
def calculate(config: CohortConfigInput):
    if not config.internal_team:
        config.internal_team = load_team_roster()
    if not config.other_external_costs:
        config.other_external_costs = [
            OtherExternalCost(**c)
            for c in load_tools_registry()["other_external_costs"]
        ]
    if not config.tools:
        config.tools = load_tools_registry()["tools"]

    engine = CohortEngine(config)
    return CalculateResponse(
        config=config,
        revenue=engine.revenue,
        costs=engine.costs,
        decisions=engine.decisions,
        pricing_tiers=engine.get_pricing_tiers(),
        sensitivity=engine.get_sensitivity(),
        annual_projection=engine.get_annual_projection(),
        career_track=next(
            (
                CareerTrackOutput(
                    key=key,
                    label=track["label"],
                    short_name=track["short_name"],
                    role_in_simulation=track["role_in_simulation"],
                    skills=track["skills"],
                    tools=[ToolBreakdownItem(**tool) for tool in track["tools"]],
                    track_total_tool_cost=track["track_total_tool_cost"],
                    track_cost_per_participant=track["track_cost_per_participant"],
                    total_tool_cost_per_user_per_month=get_tool_cost_per_user(key),
                )
                for key, track in CAREER_TRACKS.items()
                if key == config.career_track
            ),
            None,
        ),
        tool_breakdown=engine.get_tool_breakdown(),
    )


@app.post("/api/scenarios", response_model=ScenariosResponse)
def scenarios(config: CohortConfigInput):
    if not config.internal_team:
        config.internal_team = load_team_roster()
    if not config.other_external_costs:
        config.other_external_costs = [
            OtherExternalCost(**c)
            for c in load_tools_registry()["other_external_costs"]
        ]
    if not config.tools:
        config.tools = load_tools_registry()["tools"]

    return ScenarioEngine(config).generate()


@app.post("/api/sensitivity", response_model=SensitivityResponse)
def sensitivity(config: CohortConfigInput):
    if not config.internal_team:
        config.internal_team = load_team_roster()
    if not config.other_external_costs:
        config.other_external_costs = [
            OtherExternalCost(**c)
            for c in load_tools_registry()["other_external_costs"]
        ]
    if not config.tools:
        config.tools = load_tools_registry()["tools"]

    return SensitivityEngine(config).to_response()


@app.post("/api/cash-flow", response_model=CashFlowResponse)
def cash_flow(config: CohortConfigInput):
    if not config.internal_team:
        config.internal_team = load_team_roster()
    if not config.other_external_costs:
        config.other_external_costs = [
            OtherExternalCost(**c)
            for c in load_tools_registry()["other_external_costs"]
        ]
    if not config.tools:
        config.tools = load_tools_registry()["tools"]

    engine = CohortEngine(config)
    return CashFlowEngine(config, engine).to_response()


@app.post("/api/break-even", response_model=BreakEvenResponse)
def break_even(config: CohortConfigInput):
    if not config.internal_team:
        config.internal_team = load_team_roster()
    if not config.other_external_costs:
        config.other_external_costs = [
            OtherExternalCost(**c)
            for c in load_tools_registry()["other_external_costs"]
        ]
    if not config.tools:
        config.tools = load_tools_registry()["tools"]

    engine = CohortEngine(config)
    return BreakEvenEngine(config, engine).to_response()


@app.post("/api/checks", response_model=ChecksResponse)
def checks(config: CohortConfigInput):
    if not config.internal_team:
        config.internal_team = load_team_roster()
    if not config.other_external_costs:
        config.other_external_costs = [
            OtherExternalCost(**c)
            for c in load_tools_registry()["other_external_costs"]
        ]
    if not config.tools:
        config.tools = load_tools_registry()["tools"]

    engine = CohortEngine(config)
    result = calculate(config)
    scenarios_resp = ScenarioEngine(config).generate()
    cashflow = CashFlowEngine(config, engine).to_response()
    breakeven = BreakEvenEngine(config, engine).to_response()
    return ChecksEngine(config, result, scenarios_resp, cashflow, breakeven).to_response()


@app.post("/api/export/csv")
def export_csv(config: CohortConfigInput):
    if not config.internal_team:
        config.internal_team = load_team_roster()
    if not config.other_external_costs:
        config.other_external_costs = [
            OtherExternalCost(**c)
            for c in load_tools_registry()["other_external_costs"]
        ]
    if not config.tools:
        config.tools = load_tools_registry()["tools"]

    import csv
    import io

    engine = CohortEngine(config)
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Metric", "Value"])
    writer.writerow(["Participant gross receipts", engine.revenue.participant_gross_receipts])
    writer.writerow(["VAT payable", engine.revenue.vat_payable])
    writer.writerow(["Net programme revenue", engine.revenue.net_programme_revenue])
    writer.writerow(["Mentor cost", engine.costs.mentor_cost])
    writer.writerow(["M365 licences", engine.costs.m365_licences])
    writer.writerow(["Other tools", engine.costs.other_tools])
    writer.writerow(["Internal team payments", engine.costs.internal_team_payments])
    writer.writerow(["Other external costs", engine.costs.other_external_costs])
    writer.writerow(["Payment processing fees", engine.costs.payment_processing_fees])
    writer.writerow(["Contingency reserve", engine.costs.contingency_reserve])
    writer.writerow(["Total cohort cash cost", engine.costs.total_cohort_cash_cost])
    writer.writerow(["Cash surplus", engine.decisions.cash_surplus])
    writer.writerow(["Cash surplus margin", engine.decisions.cash_surplus_margin])
    writer.writerow(["Cash break-even price", engine.decisions.cash_break_even_average_price])
    writer.writerow(["Target margin price", engine.decisions.target_margin_average_price])

    output.seek(0)
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode()),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=careerleap_export.csv"},
    )
