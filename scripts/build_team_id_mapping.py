from __future__ import annotations

import json
import logging
import re
import sys
import unicodedata
from pathlib import Path
from typing import Any


ROOT_DIR = Path(__file__).resolve().parents[1]
CACHE_DIR = ROOT_DIR / "ucl_project" / ".cache"
TEAMS_PATH = ROOT_DIR / "data" / "teams.json"
MAPPING_PATH = ROOT_DIR / "data" / "team_id_mapping.json"
UNMAPPED_PATH = ROOT_DIR / "data" / "unmapped_teams.json"


logger = logging.getLogger("build_team_id_mapping")


def normalize_text(value: object) -> str:
    text = str(value or "").casefold()
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    return " ".join(re.sub(r"[^a-z0-9]+", " ", text).split())


def read_json(path: Path, fallback: object) -> object:
    if not path.exists():
        return fallback
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        logger.warning("Skipping invalid JSON: %s", path)
        return fallback


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def extract_country(team_payload: dict[str, Any]) -> str:
    country = team_payload.get("country")
    if isinstance(country, dict):
        return str(country.get("name") or country.get("alpha2") or country.get("nameCode") or "")
    if isinstance(country, str):
        return country
    return ""


def find_sofascore_teams() -> dict[int, dict[str, object]]:
    teams: dict[int, dict[str, object]] = {}
    for path in sorted(CACHE_DIR.glob("*standings_total.json")):
        payload = read_json(path, {})
        if not isinstance(payload, dict):
            continue
        standings = payload.get("standings")
        if not isinstance(standings, list):
            continue

        for group in standings:
            if not isinstance(group, dict):
                continue
            rows = group.get("rows")
            if not isinstance(rows, list):
                continue
            for row in rows:
                if not isinstance(row, dict):
                    continue
                team = row.get("team")
                if not isinstance(team, dict):
                    continue
                try:
                    sofascore_id = int(team["id"])
                except (KeyError, TypeError, ValueError):
                    continue
                if sofascore_id <= 0:
                    continue

                name = str(team.get("name") or team.get("shortName") or "").strip()
                country = extract_country(team).strip()
                if not name:
                    continue

                existing = teams.get(sofascore_id)
                if existing is None:
                    teams[sofascore_id] = {
                        "sofascore_team_id": sofascore_id,
                        "name": name,
                        "country": country,
                        "sources": [str(path.relative_to(ROOT_DIR))],
                    }
                else:
                    sources = existing.setdefault("sources", [])
                    if isinstance(sources, list):
                        source = str(path.relative_to(ROOT_DIR))
                        if source not in sources:
                            sources.append(source)
                    if not existing.get("country") and country:
                        existing["country"] = country

    logger.info("Found %d SofaScore teams in project cache", len(teams))
    return teams


def load_api_football_teams(path: Path = TEAMS_PATH) -> list[dict[str, object]]:
    raw = read_json(path, [])
    if isinstance(raw, dict):
        source = raw.values()
    elif isinstance(raw, list):
        source = raw
    else:
        source = []

    teams: list[dict[str, object]] = []
    for item in source:
        if not isinstance(item, dict):
            continue
        try:
            api_id = int(item["id"])
        except (KeyError, TypeError, ValueError):
            continue
        if api_id <= 0:
            continue
        aliases = item.get("aliases", [])
        teams.append(
            {
                "id": api_id,
                "name": str(item.get("name") or ""),
                "country": str(item.get("country") or ""),
                "aliases": [str(alias) for alias in aliases if isinstance(alias, str)] if isinstance(aliases, list) else [],
            }
        )
    logger.info("Loaded %d API-Football teams from %s", len(teams), path)
    return teams


def build_index(api_teams: list[dict[str, object]]) -> dict[tuple[str, str], list[dict[str, object]]]:
    index: dict[tuple[str, str], list[dict[str, object]]] = {}
    for team in api_teams:
        names = [str(team.get("name") or "")]
        aliases = team.get("aliases", [])
        if isinstance(aliases, list):
            names.extend(str(alias) for alias in aliases)
        country_key = normalize_text(team.get("country"))
        if not country_key:
            continue
        for name in names:
            name_key = normalize_text(name)
            if not name_key:
                continue
            index.setdefault((name_key, country_key), []).append(team)
    return index


def match_team(
    sofascore_team: dict[str, object],
    api_index: dict[tuple[str, str], list[dict[str, object]]],
) -> tuple[int | None, str]:
    name_key = normalize_text(sofascore_team.get("name"))
    country_key = normalize_text(sofascore_team.get("country"))
    if not name_key or not country_key:
        return None, "missing name or country"

    matches = api_index.get((name_key, country_key), [])
    if len(matches) == 1:
        return int(matches[0]["id"]), "exact name+country"
    if len(matches) > 1:
        return None, "ambiguous exact name+country"
    return None, "no exact name+country match"


def build_mapping() -> tuple[dict[str, int], list[dict[str, object]]]:
    sofascore_teams = find_sofascore_teams()
    api_teams = load_api_football_teams()
    api_index = build_index(api_teams)

    mapping: dict[str, int] = {}
    unmapped: list[dict[str, object]] = []

    used_api_ids: dict[int, int] = {}
    for sofascore_id, sofascore_team in sorted(sofascore_teams.items()):
        api_id, reason = match_team(sofascore_team, api_index)
        if api_id is None:
            unmapped.append({**sofascore_team, "reason": reason})
            continue
        if api_id in used_api_ids:
            unmapped.append({**sofascore_team, "reason": f"api_football_id already mapped to SofaScore {used_api_ids[api_id]}"})
            continue
        mapping[str(sofascore_id)] = api_id
        used_api_ids[api_id] = sofascore_id

    return mapping, unmapped


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    mapping, unmapped = build_mapping()
    write_json(MAPPING_PATH, {"sofascore_to_api_football": mapping})
    write_json(UNMAPPED_PATH, unmapped)
    logger.info("Mapped teams: %d", len(mapping))
    logger.info("Unmapped teams: %d", len(unmapped))
    logger.info("Saved mapping: %s", MAPPING_PATH)
    logger.info("Saved unmapped: %s", UNMAPPED_PATH)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
