from __future__ import annotations

import json
import logging
import sys
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


ROOT_DIR = Path(__file__).resolve().parents[1]
TEAMS_PATH = ROOT_DIR / "data" / "teams.json"
MISSING_LOGOS_PATH = ROOT_DIR / "data" / "missing_logos.json"
LOGO_DIR = ROOT_DIR / "assets" / "logos" / "teams"
TIMEOUT = 20


logger = logging.getLogger("download_logos")


def read_teams(path: Path = TEAMS_PATH) -> list[dict[str, object]]:
    if not path.exists():
        raise FileNotFoundError(f"{path} does not exist. Run scripts/fetch_teams.py first.")
    raw = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(raw, list):
        return [item for item in raw if isinstance(item, dict)]
    if isinstance(raw, dict):
        return [item for item in raw.values() if isinstance(item, dict)]
    raise ValueError(f"{path} must contain a list or object")


def write_missing(items: list[dict[str, object]], path: Path = MISSING_LOGOS_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(items, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def download_file(url: str, destination: Path, timeout: int = TIMEOUT) -> None:
    request = Request(
        url,
        headers={
            "user-agent": "Mozilla/5.0",
            "accept": "image/png,image/*;q=0.8,*/*;q=0.5",
        },
    )
    with urlopen(request, timeout=timeout) as response:
        content_type = response.headers.get("content-type", "")
        data = response.read()
    if not data:
        raise ValueError("empty response")
    if "image" not in content_type.lower() and not data.startswith(b"\x89PNG"):
        raise ValueError(f"unexpected content type: {content_type or 'unknown'}")
    destination.write_bytes(data)


def download_logos(teams: list[dict[str, object]]) -> int:
    LOGO_DIR.mkdir(parents=True, exist_ok=True)
    missing: list[dict[str, object]] = []
    downloaded = 0
    skipped = 0

    for team in teams:
        team_id = team.get("id")
        name = str(team.get("name") or "")
        logo_url = str(team.get("logo_url") or "")
        try:
            parsed_id = int(team_id)
        except (TypeError, ValueError):
            logger.warning("Skipping team with invalid id: %s", team)
            continue

        destination = LOGO_DIR / f"{parsed_id}.png"
        if destination.exists() and destination.stat().st_size > 0:
            skipped += 1
            logger.info("Exists: %s - %s", parsed_id, name)
            continue

        if not logo_url:
            logger.warning("Missing logo_url: %s - %s", parsed_id, name)
            missing.append({"id": parsed_id, "name": name, "reason": "missing logo_url"})
            continue

        try:
            download_file(logo_url, destination)
        except (HTTPError, URLError, TimeoutError, OSError, ValueError) as exc:
            logger.error("Failed logo %s - %s: %s", parsed_id, name, exc)
            destination.unlink(missing_ok=True)
            missing.append({"id": parsed_id, "name": name, "logo_url": logo_url, "reason": str(exc)})
            continue

        downloaded += 1
        logger.info("Downloaded: %s - %s", parsed_id, name)

    write_missing(missing)
    logger.info("Done. downloaded=%d skipped=%d missing=%d", downloaded, skipped, len(missing))
    return 0


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    try:
        teams = read_teams()
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        logger.error("%s", exc)
        return 1
    return download_logos(teams)


if __name__ == "__main__":
    raise SystemExit(main())
