import json
from pathlib import Path

_JSON_PATH = Path(__file__).parent / "career_tracks.json"


def _load_career_tracks() -> dict:
    with open(_JSON_PATH, "r") as f:
        data = json.load(f)

    tracks = {}
    for track in data["tracks"]:
        tracks[track["id"]] = {
            "label": track["name"],
            "short_name": track["short_name"],
            "role_in_simulation": track["role_in_simulation"],
            "skills": track["skills"],
            "tools": track["tools"],
            "track_total_tool_cost": track["track_total_tool_cost"],
            "track_cost_per_participant": track["track_cost_per_participant"],
        }
    return tracks


CAREER_TRACKS = _load_career_tracks()


def get_tool_cost_per_user(career_track: str) -> float:
    """Sum the monthly tool prices for a career track."""
    track = CAREER_TRACKS.get(career_track)
    if not track:
        return 0.0
    return sum(tool["cost_per_user_per_month"] for tool in track["tools"])
