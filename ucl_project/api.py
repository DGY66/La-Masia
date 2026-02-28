from __future__ import annotations

import logging
import os
import time
from datetime import datetime
from typing import Any

import requests

from config import RAPIDAPI_HOST, RAPIDAPI_BASE_URL, REQUEST_TIMEOUT
from models import Team, FormResult
from cache import get_cached, set_cached

logger = logging.getLogger(__name__)


class ApiError(Exception):
    pass


def _safe_int(value: Any, default: int = 0) -> int:
    """Safely convert any value to int with fallback"""
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _parse_form(recent_form: Any) -> list[FormResult]:
    """Parse form string/list into list of W/D/L results (last 5 matches)"""
    if isinstance(recent_form, str):
        # Handle string format like "WWLDW"
        mapping: dict[str, FormResult] = {"W": "W", "D": "D", "L": "L"}
        return [
            mapping[char]
            for char in recent_form
            if char in mapping
        ][-5:]
    elif isinstance(recent_form, list):
        # Handle list format
        mapping: dict[str, FormResult] = {"W": "W", "D": "D", "L": "L"}
        return [
            mapping[entry]
            for entry in recent_form
            if isinstance(entry, str) and entry in mapping
        ][-5:]
    return []


class UCLApiClient:
    def __init__(self, timeout: int = REQUEST_TIMEOUT) -> None:
        self._timeout = timeout
        self._api_key = os.getenv("RAPIDAPI_KEY", "")
        if not self._api_key:
            raise ApiError(
                "RAPIDAPI_KEY environment variable is not set. "
                "Set it before using the API client."
            )
        self._headers = {
            "x-rapidapi-key": self._api_key,
            "x-rapidapi-host": RAPIDAPI_HOST,
        }
        self._last_update: str | None = None
        self._is_fallback: bool = False
        self._actual_season_used: int | None = None

    def get_standings(self, season: int, fallback_season: int | None = None) -> tuple[list[Team], str | None, bool]:
        """
        Fetch UCL standings for a given season.

        Args:
            season: Primary season ID to fetch
            fallback_season: Optional fallback season ID if primary fails

        Returns:
            tuple: (teams list, last_update_timestamp, is_fallback_used)

        Raises:
            ApiError: If both primary and fallback requests fail
        """
        url = f"{RAPIDAPI_BASE_URL}/unique-tournament/7/season/{season}/standings/total"

        # Reset fallback tracking
        self._is_fallback = False
        self._actual_season_used = season

        try:
            data = self._request(url)
            teams = self._parse_standings(data)

            # Fetch form data for all teams
            logger.info(f"Fetching form data for {len(teams)} teams...")
            self._fetch_team_forms(teams)

            logger.info(f"Successfully loaded season {season}")
            return teams, self._last_update, False
        except ApiError as e:
            # If primary season fails and fallback is provided, try fallback
            if fallback_season is not None:
                logger.warning(f"⚠️  Season {season} failed ({e}), trying fallback {fallback_season}")
                fallback_url = f"{RAPIDAPI_BASE_URL}/unique-tournament/7/season/{fallback_season}/standings/total"
                try:
                    data = self._request(fallback_url)
                    teams = self._parse_standings(data)

                    # Fetch form data for all teams
                    logger.info(f"Fetching form data for {len(teams)} teams...")
                    self._fetch_team_forms(teams)

                    self._is_fallback = True
                    self._actual_season_used = fallback_season
                    logger.warning(f"⚠️  Using archived season {fallback_season} - primary season {season} not available")
                    return teams, self._last_update, True
                except ApiError as fallback_error:
                    logger.error(f"Fallback season {fallback_season} also failed: {fallback_error}")
                    raise ApiError(f"Both season {season} and fallback {fallback_season} failed") from e
            # No fallback available, re-raise original error
            raise

    def _request(self, url: str, use_cache: bool = True) -> dict[str, Any]:
        # Try cache first
        if use_cache:
            cache_key = f"api_{url.split('/')[-3]}_{url.split('/')[-2]}_{url.split('/')[-1]}"
            cached = get_cached(cache_key)
            if cached is not None:
                return cached

        try:
            response = requests.get(url, headers=self._headers, timeout=self._timeout)
            response.raise_for_status()
            payload = response.json()

            # Cache successful response
            if use_cache:
                set_cached(cache_key, payload)
        except requests.exceptions.Timeout:
            raise ApiError(f"Request timed out after {self._timeout}s")
        except requests.exceptions.HTTPError as exc:
            status = exc.response.status_code if exc.response is not None else "?"
            raise ApiError(f"HTTP {status}: {exc}")
        except requests.exceptions.ConnectionError:
            raise ApiError("Connection failed — check your network")
        except requests.exceptions.RequestException as exc:
            raise ApiError(f"Request error: {exc}")
        except ValueError as exc:
            raise ApiError(f"JSON parse error: {exc}")

        if not isinstance(payload, dict):
            raise ApiError(f"Unexpected response type: {type(payload).__name__}")

        return payload

    def _parse_standings(self, data: dict[str, Any]) -> list[Team]:
        """
        Parse SofaScore API response into Team objects.

        Expected structure:
        {
          "standings": [
            {
              "rows": [
                {
                  "team": {"name": "...", "shortName": "...", "nameCode": "..."},
                  "matches": int,
                  "wins": int,
                  "draws": int,
                  "losses": int,
                  "scoresFor": int,
                  "scoresAgainst": int,
                  "points": int,
                  "form": ["W", "D", "L", ...] or "WWLDW"
                }
              ]
            }
          ]
        }
        """
        # Extract timestamp (use current time as API doesn't provide updatedAtTimestamp)
        try:
            dt = datetime.now()
            self._last_update = dt.strftime("%d %b %Y, %H:%M")
        except Exception:
            self._last_update = None
            logger.warning("Failed to generate timestamp")

        standings = data.get("standings")
        if not isinstance(standings, list):
            logger.warning("Response missing 'standings' list — returning empty")
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
                    logger.debug("Skipping row without valid 'team' object")
                    continue

                # Extract team identifiers
                abbr_raw = t_info.get("nameCode") or t_info.get("shortName") or "??"
                abbr = str(abbr_raw)[:3].upper()  # Use 3 chars for better clarity
                name = str(t_info.get("name", "Unknown"))

                # Create team and populate all statistics
                team = Team(abbr, name)
                team.pld = _safe_int(row.get("matches"))
                team.w = _safe_int(row.get("wins"))
                team.d = _safe_int(row.get("draws"))
                team.l = _safe_int(row.get("losses"))
                team.gf = _safe_int(row.get("scoresFor"))
                team.ga = _safe_int(row.get("scoresAgainst"))

                # Always use API points if available
                api_pts = row.get("points")
                if api_pts is not None:
                    team.pts = _safe_int(api_pts)

                # Parse form (last 5 matches)
                team.form = _parse_form(row.get("form"))

                teams.append(team)

                logger.debug(
                    "Parsed team: %s - PLD:%d W:%d D:%d L:%d GF:%d GA:%d PTS:%d Form:%s",
                    name, team.pld, team.w, team.d, team.l, team.gf, team.ga, team.pts, team.form
                )

        logger.info("Parsed %d teams from API standings", len(teams))
        return teams

    def _fetch_team_forms(self, teams: list[Team]) -> None:
        """
        Fetch last 5 UCL matches for each team to determine form.

        Args:
            teams: List of Team objects to populate with form data
        """
        for idx, team in enumerate(teams):
            try:
                # Extract team ID from team object (we need to get it from the API)
                # For now, we'll fetch team events and filter UCL matches
                team_id = self._get_team_id(team.name)
                if not team_id:
                    logger.debug(f"Could not find team ID for {team.name}, skipping form")
                    continue

                # Fetch last events for this team
                url = f"{RAPIDAPI_BASE_URL}/team/{team_id}/events/last/0"
                data = self._request(url)

                # Filter UCL matches only (tournament ID = 7)
                ucl_matches = []
                for event in data.get("events", []):
                    tournament_id = event.get("tournament", {}).get("uniqueTournament", {}).get("id")
                    if tournament_id == 7:
                        # Determine if match is finished
                        status_code = event.get("status", {}).get("code")
                        if status_code != 100:  # 100 = finished
                            continue

                        home_team_id = event.get("homeTeam", {}).get("id")
                        away_team_id = event.get("awayTeam", {}).get("id")
                        home_score = event.get("homeScore", {}).get("current", 0)
                        away_score = event.get("awayScore", {}).get("current", 0)

                        # Determine result for this team
                        if home_team_id == team_id:
                            # Team played at home
                            if home_score > away_score:
                                result = "W"
                            elif home_score < away_score:
                                result = "L"
                            else:
                                result = "D"
                        elif away_team_id == team_id:
                            # Team played away
                            if away_score > home_score:
                                result = "W"
                            elif away_score < home_score:
                                result = "L"
                            else:
                                result = "D"
                        else:
                            continue

                        ucl_matches.append(result)

                        # Stop after 5 matches
                        if len(ucl_matches) >= 5:
                            break

                # Update team form (most recent first)
                team.form = ucl_matches[:5]
                logger.debug(f"Fetched form for {team.name}: {team.form}")

                # Add small delay to avoid rate limiting (every 5 teams)
                if (idx + 1) % 5 == 0:
                    time.sleep(0.5)

            except Exception as e:
                logger.warning(f"Failed to fetch form for {team.name}: {e}")
                # Keep empty form on error
                continue

    def _get_team_id(self, team_name: str) -> int | None:
        """
        Map team names to SofaScore team IDs.

        Args:
            team_name: Name of the team

        Returns:
            Team ID or None if not found
        """
        # SofaScore team IDs for major UCL clubs
        team_ids = {
            "Liverpool": 44,
            "Barcelona": 2817,
            "Arsenal": 42,
            "Inter": 2697,
            "Bayern München": 2672,
            "Real Madrid": 2829,
            "Manchester City": 17,
            "Paris Saint Germain": 1644,
            "Juventus": 2687,
            "Atletico Madrid": 2836,
            "Atalanta": 3302,
            "Bayer Leverkusen": 2681,
            "Borussia Dortmund": 2673,
            "Chelsea": 38,
            "AC Milan": 2692,
            "Tottenham Hotspur": 33,
            "Porto": 4480,
            "RB Leipzig": 6288,
            "Napoli": 2693,
            "Benfica": 3002,
            "Sporting CP": 2831,
            "PSV Eindhoven": 2382,
            "Feyenoord": 2381,
            "Monaco": 3636,
            "Eintracht Frankfurt": 2674,
            "Club Brugge": 2382,
            "Olympiacos": 3074,
            "Galatasaray": 3072,
            "Ajax": 2383,
            "Marseille": 3002,
            "Copenhagen": 3005,
            "Union SG": 2697,
            "Slavia Praha": 3147,
            "Athletic Club": 2825,
            "Newcastle": 23,
        }

        return team_ids.get(team_name)