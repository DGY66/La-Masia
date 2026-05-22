from __future__ import annotations

import argparse
import json
import logging
import os
import sys
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


ROOT_DIR = Path(__file__).resolve().parents[1]
ENV_PATH = ROOT_DIR / ".env"
TEAMS_PATH = ROOT_DIR / "data" / "teams.json"
BASE_URL = "https://v3.football.api-sports.io"
DEFAULT_LEAGUES = (2, 3, 848)  # UCL, UEL, UECL in API-Football.
TIMEOUT = 20


logger = logging.getLogger("fetch_teams")


class ApiFootballError(RuntimeError):
    pass


def load_env(path: Path = ENV_PATH) -> None:
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def get_api_key() -> str:
    load_env()
    api_key = os.getenv("API_FOOTBALL_KEY", "").strip()
    if not api_key:
        raise ApiFootballError("API_FOOTBALL_KEY is not set in .env or environment")
    return api_key


def api_get(path: str, params: dict[str, object], api_key: str, base_url: str, timeout: int) -> dict[str, Any]:
    query = urlencode({key: value for key, value in params.items() if value is not None})
    url = f"{base_url.rstrip('/')}{path}"
    if query:
        url = f"{url}?{query}"

    request = Request(
        url,
        headers={
            "x-apisports-key": api_key,
            "accept": "application/json",
        },
    )
    try:
        with urlopen(request, timeout=timeout) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        raise ApiFootballError(f"HTTP {exc.code}: {exc.reason}") from exc
    except URLError as exc:
        raise ApiFootballError(f"Connection error: {getattr(exc, 'reason', exc)}") from exc
    except TimeoutError as exc:
        raise ApiFootballError(f"Request timed out after {timeout}s") from exc
    except ValueError as exc:
        raise ApiFootballError("API returned invalid JSON") from exc

    if not isinstance(payload, dict):
        raise ApiFootballError(f"Unexpected API response type: {type(payload).__name__}")

    errors = payload.get("errors")
    if errors:
        raise ApiFootballError(f"API error: {errors}")

    return payload


def load_existing_teams(path: Path = TEAMS_PATH) -> dict[int, dict[str, object]]:
    if not path.exists():
        return {}
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except ValueError as exc:
        raise ApiFootballError(f"Invalid JSON in {path}") from exc

    teams: dict[int, dict[str, object]] = {}
    if isinstance(raw, list):
        source = raw
    elif isinstance(raw, dict):
        source = raw.values()
    else:
        raise ApiFootballError(f"{path} must contain a list or object")

    for item in source:
        if not isinstance(item, dict):
            continue
        try:
            team_id = int(item["id"])
        except (KeyError, TypeError, ValueError):
            continue
        teams[team_id] = normalize_team(item)
    return teams


def normalize_team(item: dict[str, object]) -> dict[str, object]:
    team_id = int(item["id"])
    aliases = item.get("aliases", [])
    return {
        "id": team_id,
        "name": str(item.get("name") or ""),
        "country": str(item.get("country") or ""),
        "logo_url": str(item.get("logo_url") or ""),
        "local_logo": f"assets/logos/teams/{team_id}.png",
        "aliases": aliases if isinstance(aliases, list) else [],
    }


def parse_team_response(payload: dict[str, Any]) -> list[dict[str, object]]:
    response = payload.get("response")
    if not isinstance(response, list):
        raise ApiFootballError("API response does not contain a response list")

    parsed: list[dict[str, object]] = []
    for row in response:
        if not isinstance(row, dict):
            continue
        team = row.get("team")
        if not isinstance(team, dict):
            continue
        team_id = team.get("id")
        try:
            parsed_id = int(team_id)
        except (TypeError, ValueError):
            continue
        parsed.append(
            {
                "id": parsed_id,
                "name": str(team.get("name") or ""),
                "country": str(team.get("country") or ""),
                "logo_url": str(team.get("logo") or ""),
                "local_logo": f"assets/logos/teams/{parsed_id}.png",
                "aliases": [],
            }
        )
    return parsed


def save_teams(teams: dict[int, dict[str, object]], path: Path = TEAMS_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    ordered = [teams[team_id] for team_id in sorted(teams)]
    path.write_text(json.dumps(ordered, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def fetch_teams(leagues: list[int], season: int, base_url: str, timeout: int) -> int:
    api_key = get_api_key()
    teams = load_existing_teams()
    before = len(teams)

    for league_id in leagues:
        logger.info("Fetching teams: league=%s season=%s", league_id, season)
        try:
            payload = api_get(
                "/teams",
                {"league": league_id, "season": season},
                api_key=api_key,
                base_url=base_url,
                timeout=timeout,
            )
            found = parse_team_response(payload)
        except ApiFootballError as exc:
            logger.error("Failed league=%s season=%s: %s", league_id, season, exc)
            continue

        logger.info("Found %d teams for league=%s season=%s", len(found), league_id, season)
        for team in found:
            team_id = int(team["id"])
            existing = teams.get(team_id)
            if existing:
                aliases = existing.get("aliases", [])
                team["aliases"] = aliases if isinstance(aliases, list) else []
            teams[team_id] = normalize_team(team)
            logger.info("Team: %s - %s", team_id, team["name"])

    save_teams(teams)
    added = len(teams) - before
    logger.info("Saved %d teams to %s (%d new)", len(teams), TEAMS_PATH, added)
    return 0


def current_uefa_season_start() -> int:
    from datetime import date

    today = date.today()
    return today.year if today.month >= 7 else today.year - 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Fetch teams from API-Football into data/teams.json")
    parser.add_argument("--league", action="append", type=int, dest="leagues", help="API-Football league id. Can be repeated.")
    parser.add_argument("--season", type=int, default=current_uefa_season_start(), help="Season start year, e.g. 2025 for 2025/26.")
    parser.add_argument("--base-url", default=BASE_URL)
    parser.add_argument("--timeout", type=int, default=TIMEOUT)
    return parser


def main(argv: list[str] | None = None) -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    args = build_parser().parse_args(argv)
    leagues = args.leagues or list(DEFAULT_LEAGUES)
    try:
        return fetch_teams(leagues=leagues, season=args.season, base_url=args.base_url, timeout=args.timeout)
    except ApiFootballError as exc:
        logger.error("%s", exc)
        return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
