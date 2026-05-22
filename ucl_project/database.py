from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from pathlib import Path

from espn_ids import resolve_espn_id
from models import Team
from transfermarkt_ids import resolve_transfermarkt_id


DB_PATH = Path(__file__).parent / "data" / "app.db"


def get_connection() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS standings (
                competition_key TEXT NOT NULL,
                season_key TEXT NOT NULL,
                position INTEGER NOT NULL,
                team_id INTEGER,
                abbr TEXT NOT NULL,
                name TEXT NOT NULL,
                country_name TEXT,
                country_alpha2 TEXT,
                pld INTEGER NOT NULL,
                wins INTEGER NOT NULL,
                draws INTEGER NOT NULL,
                losses INTEGER NOT NULL,
                goals_for INTEGER NOT NULL,
                goals_against INTEGER NOT NULL,
                points INTEGER NOT NULL,
                form_json TEXT NOT NULL,
                last_update TEXT,
                saved_at TEXT NOT NULL,
                PRIMARY KEY (competition_key, season_key, position)
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS user_settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
            """
        )


def save_user_settings(
    competition_key: str,
    season_key: str,
    language: str,
) -> None:
    init_db()
    values = {
        "competition_key": competition_key,
        "season_key": season_key,
        "language": language,
    }
    with get_connection() as conn:
        conn.executemany(
            """
            INSERT INTO user_settings (key, value)
            VALUES (?, ?)
            ON CONFLICT(key) DO UPDATE SET value = excluded.value
            """,
            values.items(),
        )


def load_user_settings() -> dict[str, str]:
    init_db()
    with get_connection() as conn:
        rows = conn.execute("SELECT key, value FROM user_settings").fetchall()
    return {row["key"]: row["value"] for row in rows}


def save_standings(
    competition_key: str,
    season_key: str,
    teams: list[Team],
    last_update: str | None,
) -> None:
    if not teams:
        return

    init_db()
    saved_at = datetime.now().isoformat(timespec="seconds")
    sorted_teams = sorted(teams, key=lambda team: team.sort_key())

    with get_connection() as conn:
        conn.execute(
            "DELETE FROM standings WHERE competition_key = ? AND season_key = ?",
            (competition_key, season_key),
        )
        conn.executemany(
            """
            INSERT INTO standings (
                competition_key, season_key, position, team_id, abbr, name,
                country_name, country_alpha2, pld, wins, draws, losses,
                goals_for, goals_against, points, form_json, last_update, saved_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    competition_key,
                    season_key,
                    position,
                    team.team_id,
                    team.abbr,
                    team.name,
                    team.country_name,
                    team.country_alpha2,
                    team.pld,
                    team.w,
                    team.d,
                    team.l,
                    team.gf,
                    team.ga,
                    team.pts,
                    json.dumps(team.form),
                    last_update,
                    saved_at,
                )
                for position, team in enumerate(sorted_teams, start=1)
            ],
        )


def load_standings(competition_key: str, season_key: str) -> tuple[list[Team], str | None]:
    init_db()
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT *
            FROM standings
            WHERE competition_key = ? AND season_key = ?
            ORDER BY position
            """,
            (competition_key, season_key),
        ).fetchall()

    teams: list[Team] = []
    last_update: str | None = None
    for row in rows:
        team = Team(
            abbr=row["abbr"],
            name=row["name"],
            team_id=row["team_id"],
            country_name=row["country_name"],
            country_alpha2=row["country_alpha2"],
            espn_id=resolve_espn_id(row["name"]),
            transfermarkt_id=resolve_transfermarkt_id(row["name"]),
        )
        team.pld = row["pld"]
        team.w = row["wins"]
        team.d = row["draws"]
        team.l = row["losses"]
        team.gf = row["goals_for"]
        team.ga = row["goals_against"]
        team.pts = row["points"]
        team.form = _parse_form_json(row["form_json"])
        teams.append(team)
        last_update = row["last_update"] or row["saved_at"]

    return teams, last_update


def _parse_form_json(value: str) -> list[str]:
    try:
        parsed = json.loads(value)
    except json.JSONDecodeError:
        return []
    if not isinstance(parsed, list):
        return []
    return [item for item in parsed if item in {"W", "D", "L"}]
