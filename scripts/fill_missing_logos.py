from __future__ import annotations

import argparse
import json
import logging
import re
import sys
import time
from pathlib import Path
from typing import Any
from urllib.parse import urlencode
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from build_team_id_mapping import (
    MAPPING_PATH,
    ROOT_DIR,
    find_sofascore_teams,
    normalize_text,
    read_json,
    write_json,
)
from download_logos import LOGO_DIR, download_file
from fetch_teams import BASE_URL, TIMEOUT, ApiFootballError, api_get, get_api_key


UNRESOLVED_PATH = ROOT_DIR / "data" / "unresolved_logo_teams.json"
REPORT_PATH = ROOT_DIR / "data" / "logo_fill_report.json"
TEAMS_PATH = ROOT_DIR / "data" / "teams.json"
EXTERNAL_LOGO_DIR = LOGO_DIR / "external"
THESPORTSDB_SEARCH_URL = "https://www.thesportsdb.com/api/v1/json/3/searchteams.php"


logger = logging.getLogger("fill_missing_logos")

TEAM_SEARCH_ALIASES: dict[str, list[str]] = {
    "Brighton & Hove Albion": ["Brighton"],
    "Tottenham Hotspur": ["Tottenham"],
    "West Ham United": ["West Ham"],
    "Newcastle United": ["Newcastle"],
    "Liverpool FC": ["Liverpool"],
    "Bodø/Glimt": ["Bodo/Glimt", "Bodoe/Glimt"],
    "Molde FK": ["Molde"],
    "SK Brann": ["Brann"],
    "FC København": ["Copenhagen", "Kobenhavn"],
    "FC Nordsjælland": ["Nordsjaelland"],
    "Olympique de Marseille": ["Marseille"],
    "Olympique Lyonnais": ["Lyon"],
    "AS Monaco": ["Monaco"],
    "Stade Rennais": ["Rennes"],
    "RC Strasbourg": ["Strasbourg"],
    "Stade Brestois": ["Brest"],
    "Djurgårdens IF": ["Djurgarden"],
    "BK Häcken": ["Hacken"],
    "Malmö FF": ["Malmo FF", "Malmo"],
}


def load_mapping() -> tuple[dict[str, int], dict[str, str]]:
    payload = read_json(MAPPING_PATH, {"sofascore_to_api_football": {}, "sofascore_to_external_logo": {}})
    raw = payload.get("sofascore_to_api_football") if isinstance(payload, dict) else {}
    if not isinstance(raw, dict):
        raw = {}
    raw_external = payload.get("sofascore_to_external_logo") if isinstance(payload, dict) else {}
    if not isinstance(raw_external, dict):
        raw_external = {}

    mapping: dict[str, int] = {}
    for key, value in raw.items():
        try:
            sofascore_id = int(key)
            api_id = int(value)
        except (TypeError, ValueError):
            continue
        if sofascore_id > 0 and api_id > 0:
            mapping[str(sofascore_id)] = api_id
    external: dict[str, str] = {}
    for key, value in raw_external.items():
        try:
            sofascore_id = int(key)
        except (TypeError, ValueError):
            continue
        if sofascore_id > 0 and isinstance(value, str) and value:
            external[str(sofascore_id)] = value
    return mapping, external


def save_mapping(mapping: dict[str, int], external_mapping: dict[str, str]) -> None:
    ordered = {key: mapping[key] for key in sorted(mapping, key=lambda value: int(value))}
    ordered_external = {key: external_mapping[key] for key in sorted(external_mapping, key=lambda value: int(value))}
    write_json(
        MAPPING_PATH,
        {
            "sofascore_to_api_football": ordered,
            "sofascore_to_external_logo": ordered_external,
        },
    )


def save_progress(
    mapping: dict[str, int],
    external_mapping: dict[str, str],
    unresolved: list[dict[str, object]],
    report: dict[str, object],
) -> None:
    save_mapping(mapping, external_mapping)
    write_json(UNRESOLVED_PATH, unresolved)
    write_json(REPORT_PATH, report)


def load_known_api_teams() -> dict[int, dict[str, object]]:
    raw = read_json(TEAMS_PATH, [])
    if isinstance(raw, dict):
        source = raw.values()
    elif isinstance(raw, list):
        source = raw
    else:
        source = []

    teams: dict[int, dict[str, object]] = {}
    for item in source:
        if not isinstance(item, dict):
            continue
        try:
            team_id = int(item["id"])
        except (KeyError, TypeError, ValueError):
            continue
        if team_id > 0:
            teams[team_id] = item
    return teams


def logo_exists(api_football_id: int | None) -> bool:
    if api_football_id is None:
        return False
    path = LOGO_DIR / f"{api_football_id}.png"
    return path.exists() and path.stat().st_size > 0


def external_logo_exists(path_value: str | None) -> bool:
    if not path_value:
        return False
    path = ROOT_DIR / path_value
    return path.exists() and path.stat().st_size > 0


def api_team_candidates(payload: dict[str, Any]) -> list[dict[str, object]]:
    response = payload.get("response")
    if not isinstance(response, list):
        return []

    teams: list[dict[str, object]] = []
    for row in response:
        if not isinstance(row, dict):
            continue
        team = row.get("team")
        if not isinstance(team, dict):
            continue
        try:
            team_id = int(team["id"])
        except (KeyError, TypeError, ValueError):
            continue
        if team_id <= 0:
            continue
        teams.append(
            {
                "id": team_id,
                "name": str(team.get("name") or ""),
                "country": str(team.get("country") or ""),
                "logo_url": str(team.get("logo") or ""),
                "aliases": [],
            }
        )
    return teams


def candidate_names(candidate: dict[str, object], known_api_teams: dict[int, dict[str, object]]) -> list[str]:
    names = [str(candidate.get("name") or "")]
    known = known_api_teams.get(int(candidate["id"]))
    if isinstance(known, dict):
        aliases = known.get("aliases", [])
        if isinstance(aliases, list):
            names.extend(str(alias) for alias in aliases if isinstance(alias, str))
    return names


def is_confident_match(
    project_team: dict[str, object],
    candidate: dict[str, object],
    known_api_teams: dict[int, dict[str, object]],
) -> bool:
    project_names = project_match_names(project_team)
    project_country = normalize_text(project_team.get("country"))
    candidate_country = normalize_text(candidate.get("country"))
    if not project_names or not project_country or project_country != candidate_country:
        return False

    return any(normalize_text(name) in project_names for name in candidate_names(candidate, known_api_teams))


def choose_candidate(
    project_team: dict[str, object],
    candidates: list[dict[str, object]],
    known_api_teams: dict[int, dict[str, object]],
) -> tuple[dict[str, object] | None, str]:
    confident = [
        candidate
        for candidate in candidates
        if is_confident_match(project_team, candidate, known_api_teams)
    ]
    if len(confident) == 1:
        return confident[0], "exact name/alias + country"
    if len(confident) > 1:
        return None, "ambiguous exact name/alias + country"
    if not candidates:
        return None, "no API-Football candidates"
    return None, "no confident name/alias + country match"


def search_team(team_name: str, api_key: str) -> list[dict[str, object]]:
    query = search_query(team_name)
    if not query:
        return []
    payload = api_get(
        "/teams",
        {"search": query},
        api_key=api_key,
        base_url=BASE_URL,
        timeout=TIMEOUT,
    )
    return api_team_candidates(payload)


def project_match_names(project_team: dict[str, object]) -> set[str]:
    names = [str(project_team.get("name") or "")]
    aliases = project_team.get("aliases", [])
    if isinstance(aliases, list):
        names.extend(str(alias) for alias in aliases if isinstance(alias, str))
    for alias in TEAM_SEARCH_ALIASES.get(str(project_team.get("name") or ""), []):
        names.append(alias)
    return {normalize_text(name) for name in names if normalize_text(name)}


def search_names(project_team: dict[str, object]) -> list[str]:
    names = [str(project_team.get("name") or "").strip()]
    names.extend(TEAM_SEARCH_ALIASES.get(names[0], []))
    unique: list[str] = []
    seen: set[str] = set()
    for name in names:
        key = normalize_text(name)
        if not key or key in seen:
            continue
        seen.add(key)
        unique.append(name)
    return unique


def search_api_football_for_team(project_team: dict[str, object], api_key: str) -> tuple[list[dict[str, object]], str]:
    all_candidates: list[dict[str, object]] = []
    used_queries: list[str] = []
    seen_ids: set[int] = set()
    for name in search_names(project_team):
        candidates = search_team(name, api_key)
        used_queries.append(name)
        for candidate in candidates:
            candidate_id = int(candidate["id"])
            if candidate_id in seen_ids:
                continue
            seen_ids.add(candidate_id)
            all_candidates.append(candidate)
    return all_candidates, ", ".join(used_queries)


def search_query(team_name: str) -> str:
    return " ".join(re.sub(r"[^A-Za-z0-9 ]+", " ", team_name).split())


def is_rate_limit_error(exc: BaseException) -> bool:
    if isinstance(exc, HTTPError) and exc.code == 429:
        return True
    return "HTTP 429" in str(exc) or "Too Many Requests" in str(exc)


def safe_logo_name(team_name: str) -> str:
    value = normalize_text(team_name).replace(" ", "_")
    return value or "team"


def save_logo(candidate: dict[str, object]) -> None:
    LOGO_DIR.mkdir(parents=True, exist_ok=True)
    api_id = int(candidate["id"])
    logo_url = str(candidate.get("logo_url") or "")
    if not logo_url:
        raise ValueError("missing logo_url")
    destination = LOGO_DIR / f"{api_id}.png"
    if destination.exists() and destination.stat().st_size > 0:
        return
    download_file(logo_url, destination, timeout=TIMEOUT)


def search_thesportsdb(team_name: str) -> list[dict[str, object]]:
    query = search_query(team_name)
    if not query:
        return []
    url = f"{THESPORTSDB_SEARCH_URL}?{urlencode({'t': query})}"
    request = Request(url, headers={"accept": "application/json", "user-agent": "Mozilla/5.0"})
    with urlopen(request, timeout=TIMEOUT) as response:
        payload = json.loads(response.read().decode("utf-8"))
    teams = payload.get("teams") if isinstance(payload, dict) else None
    if not isinstance(teams, list):
        return []
    parsed: list[dict[str, object]] = []
    for item in teams:
        if not isinstance(item, dict):
            continue
        parsed.append(
            {
                "name": str(item.get("strTeam") or ""),
                "country": str(item.get("strCountry") or ""),
                "badge_url": str(item.get("strTeamBadge") or ""),
            }
        )
    return parsed


def choose_external_candidate(project_team: dict[str, object], candidates: list[dict[str, object]]) -> tuple[dict[str, object] | None, str]:
    project_names = project_match_names(project_team)
    project_country = normalize_text(project_team.get("country"))
    confident = [
        candidate
        for candidate in candidates
        if normalize_text(candidate.get("name")) in project_names
        and normalize_text(candidate.get("country")) == project_country
        and str(candidate.get("badge_url") or "")
    ]
    if len(confident) == 1:
        return confident[0], "TheSportsDB exact name + country"
    if len(confident) > 1:
        return None, "TheSportsDB ambiguous exact name + country"
    if not candidates:
        return None, "TheSportsDB no candidates"
    return None, "TheSportsDB no confident name + country match"


def save_external_logo(team_name: str, candidate: dict[str, object]) -> str:
    EXTERNAL_LOGO_DIR.mkdir(parents=True, exist_ok=True)
    relative_path = Path("assets") / "logos" / "teams" / "external" / f"{safe_logo_name(team_name)}.png"
    destination = ROOT_DIR / relative_path
    if destination.exists() and destination.stat().st_size > 0:
        return relative_path.as_posix()
    download_file(str(candidate.get("badge_url") or ""), destination, timeout=TIMEOUT)
    return relative_path.as_posix()


def fill_missing_logos(limit: int | None = None, delay: float = 8.0) -> dict[str, object]:
    api_key = get_api_key()
    teams = find_sofascore_teams()
    mapping, external_mapping = load_mapping()
    known_api_teams = load_known_api_teams()

    checked = len(teams)
    existing = sum(
        1
        for sofascore_id in teams
        if logo_exists(mapping.get(str(sofascore_id))) or external_logo_exists(external_mapping.get(str(sofascore_id)))
    )
    downloaded = 0
    searched = 0
    external_searched = 0
    rate_limit_reached = False
    unresolved: list[dict[str, object]] = []
    resolved: list[dict[str, object]] = []

    def current_report() -> dict[str, object]:
        return {
            "checked": checked,
            "existing_logos": existing,
            "downloaded": downloaded,
            "unresolved": len(unresolved),
            "searched": searched,
            "external_searched": external_searched,
            "limit": limit,
            "delay": delay,
            "rate_limit_reached": rate_limit_reached,
            "resolved": resolved,
        }

    sorted_teams = sorted(teams.items())
    for sofascore_id, team in sorted_teams:
        mapping_key = str(sofascore_id)
        mapped_api_id = mapping.get(mapping_key)
        if logo_exists(mapped_api_id):
            continue
        if external_logo_exists(external_mapping.get(mapping_key)):
            continue

        if limit is not None and searched >= limit:
            logger.info("Limit reached: %d", limit)
            break

        team_name = str(team.get("name") or "").strip()
        if not team_name:
            unresolved.append({**team, "reason": "missing project team name"})
            continue

        if searched > 0 and delay > 0:
            time.sleep(delay)

        searched += 1
        logger.info("Searching logo: %s - %s", sofascore_id, team_name)
        try:
            candidates, queries = search_api_football_for_team(team, api_key)
            candidate, reason = choose_candidate(team, candidates, known_api_teams)
        except (ApiFootballError, HTTPError, URLError, TimeoutError, OSError, ValueError) as exc:
            unresolved.append({**team, "reason": f"API/search error: {exc}"})
            logger.error("Search failed for %s - %s: %s", sofascore_id, team_name, exc)
            if is_rate_limit_error(exc):
                rate_limit_reached = True
                logger.warning("rate limit reached")
                save_progress(mapping, external_mapping, unresolved, current_report())
                break
            continue

        if candidate is None:
            if delay > 0:
                time.sleep(delay)
            external_searched += 1
            try:
                external_candidates = []
                seen_external: set[tuple[str, str]] = set()
                for external_name in search_names(team):
                    for item in search_thesportsdb(external_name):
                        key = (str(item.get("name") or ""), str(item.get("country") or ""))
                        if key in seen_external:
                            continue
                        seen_external.add(key)
                        external_candidates.append(item)
                external_candidate, external_reason = choose_external_candidate(team, external_candidates)
            except (HTTPError, URLError, TimeoutError, OSError, ValueError) as exc:
                unresolved.append({**team, "reason": f"{reason}; TheSportsDB error: {exc}"})
                continue

            if external_candidate is None:
                unresolved.append(
                    {
                        **team,
                        "reason": f"{reason}; {external_reason}",
                        "search_queries": queries,
                        "api_football_candidates": [
                            {
                                "api_football_id": item.get("id"),
                                "name": item.get("name"),
                                "country": item.get("country"),
                            }
                            for item in candidates[:10]
                        ],
                        "external_candidates": [
                            {
                                "name": item.get("name"),
                                "country": item.get("country"),
                            }
                            for item in external_candidates[:10]
                        ],
                    }
                )
                continue

            try:
                external_path = save_external_logo(team_name, external_candidate)
            except (HTTPError, URLError, TimeoutError, OSError, ValueError) as exc:
                unresolved.append({**team, "reason": f"{reason}; TheSportsDB logo download error: {exc}"})
                continue

            external_mapping[mapping_key] = external_path
            downloaded += 1
            resolved.append(
                {
                    "sofascore_team_id": sofascore_id,
                    "name": team_name,
                    "country": team.get("country"),
                    "external_logo": external_path,
                    "external_name": external_candidate.get("name"),
                    "reason": external_reason,
                }
            )
            logger.info("Resolved external: %s -> %s", sofascore_id, external_path)
            save_progress(mapping, external_mapping, unresolved, current_report())
            continue

        try:
            save_logo(candidate)
        except (HTTPError, URLError, TimeoutError, OSError, ValueError) as exc:
            unresolved.append(
                {
                    **team,
                    "api_football_id": candidate.get("id"),
                    "api_football_name": candidate.get("name"),
                    "reason": f"logo download error: {exc}",
                }
            )
            logger.error("Download failed for %s - %s: %s", sofascore_id, team_name, exc)
            continue

        api_id = int(candidate["id"])
        mapping[mapping_key] = api_id
        downloaded += 1
        resolved.append(
            {
                "sofascore_team_id": sofascore_id,
                "name": team_name,
                "country": team.get("country"),
                "api_football_id": api_id,
                "api_football_name": candidate.get("name"),
                "reason": reason,
            }
        )
        logger.info("Resolved: %s -> %s (%s)", sofascore_id, api_id, candidate.get("name"))
        save_progress(mapping, external_mapping, unresolved, current_report())

    report = current_report()
    save_progress(mapping, external_mapping, unresolved, report)
    return report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Fill missing local team logos via API-Football search.")
    parser.add_argument("--delay", type=float, default=8.0, help="Delay in seconds between API requests.")
    parser.add_argument("--limit", type=int, default=None, help="Process only N missing teams in this run.")
    return parser


def main(argv: list[str] | None = None) -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    args = build_parser().parse_args(argv)
    if args.limit is not None and args.limit < 1:
        logger.error("--limit must be greater than 0")
        return 1
    if args.delay < 0:
        logger.error("--delay must be >= 0")
        return 1
    try:
        report = fill_missing_logos(limit=args.limit, delay=args.delay)
    except ApiFootballError as exc:
        logger.error("%s", exc)
        return 1
    logger.info("Checked: %d", report["checked"])
    logger.info("Existing logos: %d", report["existing_logos"])
    logger.info("Downloaded: %d", report["downloaded"])
    logger.info("Unresolved: %d", report["unresolved"])
    logger.info("Searched this run: %d", report["searched"])
    if report.get("rate_limit_reached"):
        logger.warning("rate limit reached")
    logger.info("Saved report: %s", REPORT_PATH)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
