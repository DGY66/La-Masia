from __future__ import annotations

import logging
import os
import json
import subprocess
from datetime import datetime
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from cache import get_cached, set_cached
from config import CompetitionConfig, RAPIDAPI_BASE_URL, RAPIDAPI_HOST, REQUEST_TIMEOUT
from espn_ids import resolve_espn_id
from models import FormResult, Team
from sofascore_ids import resolve_sofascore_id
from transfermarkt_ids import resolve_transfermarkt_id

logger = logging.getLogger(__name__)

PUBLIC_HEADERS = {
    "accept": "application/json, text/plain, */*",
    "accept-language": "en-US,en;q=0.9",
    "cache-control": "no-cache",
    "pragma": "no-cache",
    "referer": "https://www.sofascore.com/",
    "user-agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/136.0.0.0 Safari/537.36"
    ),
}


class ApiError(Exception):
    pass


class NoSeasonDataError(ApiError):
    pass


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _parse_form(recent_form: Any) -> list[FormResult]:
    mapping: dict[str, FormResult] = {"W": "W", "D": "D", "L": "L"}
    if isinstance(recent_form, str):
        return [mapping[char] for char in recent_form if char in mapping][-5:]
    if isinstance(recent_form, list):
        return [
            mapping[entry]
            for entry in recent_form
            if isinstance(entry, str) and entry in mapping
        ][-5:]
    return []


class SofaScoreApiClient:
    def __init__(self, timeout: int = REQUEST_TIMEOUT) -> None:
        self._timeout = timeout
        self._api_key = os.getenv("RAPIDAPI_KEY", "")
        self._endpoints: list[tuple[str, dict[str, str]]] = []

        if self._api_key:
            self._endpoints.append((
                RAPIDAPI_BASE_URL,
                {
                    "x-rapidapi-key": self._api_key,
                    "x-rapidapi-host": RAPIDAPI_HOST,
                    **PUBLIC_HEADERS,
                },
            ))

        # Public SofaScore endpoints work without RapidAPI in many environments.
        self._endpoints.extend([
            ("https://www.sofascore.com/api/v1", dict(PUBLIC_HEADERS)),
            ("https://api.sofascore.com/api/v1", dict(PUBLIC_HEADERS)),
        ])
        self._last_update: str | None = None

    def get_standings(
        self,
        competition: CompetitionConfig,
        season_key: str = "2526",
    ) -> tuple[list[Team], str | None, bool]:
        season_candidates = self._resolve_season_candidates(competition, season_key)
        last_error: ApiError | None = None

        for index, season_id in enumerate(season_candidates):
            path = (
                f"/unique-tournament/"
                f"{competition.tournament_id}/season/{season_id}/standings/total"
            )
            try:
                data = self._request(path)
                teams = self._parse_standings(data, competition.key)
                if not teams:
                    data = self._request(path, use_cache=False)
                    teams = self._parse_standings(data, competition.key)
                if not teams:
                    raise ApiError(f"Empty standings payload for season {season_id}")
                is_fallback = index > 0
                logger.info(
                    "Loaded %s standings using season %s (%s teams)",
                    competition.short_title,
                    season_id,
                    len(teams),
                )
                return teams, self._last_update, is_fallback
            except ApiError as exc:
                last_error = exc
                logger.warning(
                    "Failed loading %s season %s: %s",
                    competition.short_title,
                    season_id,
                    exc,
                )

        if last_error is None:
            raise ApiError(f"No season candidates available for {competition.short_title}")
        raise last_error

    def _resolve_season_candidates(
        self,
        competition: CompetitionConfig,
        season_key: str = "2526",
    ) -> list[int]:
        """Return a list of season IDs matching the requested season_key."""
        if competition.key == "uecl" and _safe_int(season_key, 0) < 2122:
            raise NoSeasonDataError(f"{competition.short_title} has no data before 2021/22")

        candidates: list[int] = []

        # Convert "1516" to variants like "15/16", "2015/16", "2015/2016"
        s1 = season_key[:2]
        s2 = season_key[2:]
        target_name_1 = f"{s1}/{s2}"
        target_name_2 = f"20{s1}/{s2}"
        target_name_3 = f"20{s1}/20{s2}"
        target_name_4 = f"{s1}/20{s2}"

        try:
            data = self._request(f"/unique-tournament/{competition.tournament_id}/seasons")
            raw_seasons = data.get("seasons")
            if isinstance(raw_seasons, list):
                for season in raw_seasons:
                    if not isinstance(season, dict): continue
                    name = str(season.get("name", ""))
                    season_id = season.get("id")
                    if not isinstance(season_id, int): continue

                    if (target_name_1 in name or target_name_2 in name or 
                        target_name_3 in name or target_name_4 in name):
                        candidates.append(season_id)
        except ApiError:
            pass
            
        if candidates:
            return list(dict.fromkeys(candidates))

        # Fallback to predefined if current or archive
        if season_key == "2526":
            if competition.preferred_season_id is not None:
                candidates.append(competition.preferred_season_id)
            if competition.fallback_season_id is not None:
                candidates.append(competition.fallback_season_id)
        elif season_key == "2425":
            if competition.archive_preferred_season_id is not None:
                candidates.append(competition.archive_preferred_season_id)
            if competition.archive_fallback_season_id is not None:
                candidates.append(competition.archive_fallback_season_id)

        if candidates:
            return list(dict.fromkeys(candidates))

        # Ultimate fallback
        seasons = self._fetch_seasons(competition.tournament_id)
        if not seasons:
            raise ApiError(f"Could not resolve season IDs for {competition.short_title}")
        return seasons[:2]

    def _fetch_seasons(self, tournament_id: int) -> list[int]:
        data = self._request(f"/unique-tournament/{tournament_id}/seasons")

        raw_seasons = data.get("seasons")
        if not isinstance(raw_seasons, list):
            raise ApiError(f"Unexpected seasons payload for tournament {tournament_id}")

        parsed: list[tuple[int, int, int]] = []
        for season in raw_seasons:
            if not isinstance(season, dict):
                continue
            season_id = season.get("id")
            if not isinstance(season_id, int):
                continue
            year = _safe_int(season.get("year"), 0)
            name = str(season.get("name", ""))
            parsed.append((year, self._extract_season_order(name), season_id))

        parsed.sort(reverse=True)
        return [season_id for _, _, season_id in parsed]

    @staticmethod
    def _extract_season_order(name: str) -> int:
        digits = "".join(ch for ch in name if ch.isdigit())
        if not digits:
            return 0
        try:
            return int(digits)
        except ValueError:
            return 0

    def _request(self, path: str, use_cache: bool = True) -> dict[str, Any]:
        cache_key = None
        if use_cache:
            cache_key = (
                path.strip("/")
                .replace("/", "_")
                .replace("?", "_")
                .replace("&", "_")
                .replace("=", "_")
            )
            cached = get_cached(cache_key)
            if cached is not None:
                return cached

        last_error: ApiError | None = None
        for base_url, headers in self._endpoints:
            try:
                request = Request(f"{base_url}{path}", headers=headers)
                with urlopen(request, timeout=self._timeout) as response:
                    payload = json.loads(response.read().decode("utf-8"))
                if cache_key is not None:
                    set_cached(cache_key, payload)
                break
            except TimeoutError:
                last_error = ApiError(f"Request timed out after {self._timeout}s")
            except HTTPError as exc:
                if exc.code == 403:
                    try:
                        payload = self._request_with_curl(f"{base_url}{path}", headers)
                        if cache_key is not None:
                            set_cached(cache_key, payload)
                        break
                    except ApiError as curl_exc:
                        last_error = curl_exc
                        continue
                last_error = ApiError(f"HTTP {exc.code}: {exc.reason}")
            except URLError as exc:
                reason = getattr(exc, "reason", exc)
                last_error = ApiError(f"Connection failed - {reason}")
            except ValueError as exc:
                last_error = ApiError(f"JSON parse error: {exc}")
        else:
            if last_error is None:
                raise ApiError("Request failed")
            raise last_error

        if not isinstance(payload, dict):
            raise ApiError(f"Unexpected response type: {type(payload).__name__}")

        return payload

    def _request_with_curl(self, url: str, headers: dict[str, str]) -> dict[str, Any]:
        command = ["curl.exe", "-s", "-L", url]
        for key, value in headers.items():
            command.extend(["-H", f"{key}: {value}"])

        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=self._timeout,
                check=False,
            )
        except FileNotFoundError as exc:
            raise ApiError("curl.exe is not available") from exc
        except subprocess.TimeoutExpired as exc:
            raise ApiError(f"curl timed out after {self._timeout}s") from exc

        if result.returncode != 0:
            stderr = (result.stderr or "").strip()
            raise ApiError(
                f"curl failed with exit code {result.returncode}: {stderr or 'no output'}"
            )

        try:
            payload = json.loads(result.stdout)
        except ValueError as exc:
            raise ApiError("curl returned invalid JSON") from exc

        if not isinstance(payload, dict):
            raise ApiError(f"Unexpected curl response type: {type(payload).__name__}")
        return payload

    def _parse_standings(self, data: dict[str, Any], competition_key: str) -> list[Team]:
        self._last_update = self._extract_timestamp(data)
        standings = data.get("standings")
        if not isinstance(standings, list):
            logger.warning("Response missing 'standings' list")
            return []

        teams: list[Team] = []
        for group in standings:
            if not isinstance(group, dict):
                continue

            rows = group.get("rows")
            if not isinstance(rows, list):
                continue

            for row in rows:
                if not isinstance(row, dict):
                    continue

                t_info = row.get("team")
                if not isinstance(t_info, dict):
                    continue

                country_info = t_info.get("country")
                country_name = None
                country_alpha2 = None
                if isinstance(country_info, dict):
                    raw_country_name = country_info.get("name")
                    raw_alpha2 = (
                        country_info.get("alpha2")
                        or country_info.get("alpha2Code")
                        or country_info.get("nameCode")
                    )
                    if isinstance(raw_country_name, str) and raw_country_name.strip():
                        country_name = raw_country_name.strip()
                    if isinstance(raw_alpha2, str) and raw_alpha2.strip():
                        country_alpha2 = raw_alpha2.strip()

                raw_name = str(t_info.get("name", "Unknown"))
                raw_short_name = t_info.get("shortName")
                raw_name_code = t_info.get("nameCode")
                raw_slug = t_info.get("slug")
                raw_team_id = _safe_int(t_info.get("id"), 0) or resolve_sofascore_id(
                    raw_name,
                    str(raw_short_name) if raw_short_name is not None else None,
                    str(raw_name_code) if raw_name_code is not None else None,
                    str(raw_slug) if raw_slug is not None else None,
                )
                team = Team(
                    abbr=str(raw_name_code or raw_short_name or "??")[:3].upper(),
                    name=raw_name,
                    team_id=raw_team_id,
                    country_name=country_name,
                    country_alpha2=country_alpha2,
                    espn_id=resolve_espn_id(
                        raw_name,
                        str(raw_short_name) if raw_short_name is not None else None,
                        str(raw_name_code) if raw_name_code is not None else None,
                        str(raw_slug) if raw_slug is not None else None,
                    ),
                    transfermarkt_id=resolve_transfermarkt_id(raw_name),
                )
                team.pld = _safe_int(row.get("matches"))
                team.w = _safe_int(row.get("wins"))
                team.d = _safe_int(row.get("draws"))
                team.l = _safe_int(row.get("losses"))
                team.gf = _safe_int(row.get("scoresFor"))
                team.ga = _safe_int(row.get("scoresAgainst"))

                points = row.get("points")
                if points is not None:
                    team.pts = _safe_int(points)

                team.form = _parse_form(row.get("form"))
                teams.append(team)

        logger.info("Parsed %d teams from standings", len(teams))
        return teams

    @staticmethod
    def _extract_timestamp(data: dict[str, Any]) -> str:
        for key in ("updatedAt", "updatedAtTimestamp", "generatedAt"):
            raw = data.get(key)
            if isinstance(raw, (int, float)):
                if raw > 10_000_000_000:
                    raw = raw / 1000
                try:
                    return datetime.fromtimestamp(raw).strftime("%d %b %Y, %H:%M")
                except (OverflowError, OSError, ValueError):
                    continue
            if isinstance(raw, str):
                try:
                    return datetime.fromisoformat(raw.replace("Z", "+00:00")).strftime("%d %b %Y, %H:%M")
                except ValueError:
                    continue
        return datetime.now().strftime("%d %b %Y, %H:%M")
