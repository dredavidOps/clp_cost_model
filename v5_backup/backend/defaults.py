"""
Load default configuration values from JSON files.
"""

import json
from pathlib import Path

from backend.models import CohortConfigInput, InternalTeamMember, OtherExternalCost, SeatMix, WorkstreamConfig


_DATA_DIR = Path(__file__).parent


def _load_json(filename: str) -> dict:
    with open(_DATA_DIR / filename, "r") as f:
        return json.load(f)


def load_team_roster() -> list:
    data = _load_json("team_roster.json")
    return [InternalTeamMember(**m) for m in data["members"]]


def load_tools_registry() -> dict:
    return _load_json("tools_registry.json")


def load_pricing_tiers() -> dict:
    return _load_json("pricing_tiers.json")


def build_default_config() -> CohortConfigInput:
    """Return a CohortConfigInput populated from JSON defaults."""
    tools_reg = load_tools_registry()
    pricing = load_pricing_tiers()
    roster = load_team_roster()

    return CohortConfigInput(
        workstreams=WorkstreamConfig(),
        seat_mix=SeatMix(**pricing["seat_mix"]),
        internal_team=roster,
        other_external_costs=[
            OtherExternalCost(**c) for c in tools_reg["other_external_costs"]
        ],
        tools=tools_reg["tools"],
        m365_price_per_account_per_month=tools_reg["m365"]["price_per_account_per_month"],
    )
