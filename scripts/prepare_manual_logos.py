from __future__ import annotations

import json
import logging
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
UNRESOLVED_PATH = ROOT_DIR / "data" / "unresolved_logo_teams.json"
TEMPLATE_PATH = ROOT_DIR / "data" / "manual_logos_template.json"


logger = logging.getLogger("prepare_manual_logos")


def read_unresolved() -> list[dict[str, object]]:
    if not UNRESOLVED_PATH.exists():
        return []
    raw = json.loads(UNRESOLVED_PATH.read_text(encoding="utf-8"))
    return [item for item in raw if isinstance(item, dict)] if isinstance(raw, list) else []


def build_template(unresolved: list[dict[str, object]]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    seen: set[str] = set()
    for item in unresolved:
        sofascore_id = item.get("sofascore_team_id") or item.get("sofascore_id")
        if sofascore_id is None:
            continue
        key = str(sofascore_id)
        if key in seen:
            continue
        seen.add(key)
        rows.append(
            {
                "sofascore_id": key,
                "name": str(item.get("name") or ""),
                "country": str(item.get("country") or ""),
                "manual_logo": "",
            }
        )
    return rows


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    template = build_template(read_unresolved())
    TEMPLATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    TEMPLATE_PATH.write_text(json.dumps(template, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    logger.info("Saved %d unresolved teams to %s", len(template), TEMPLATE_PATH)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
