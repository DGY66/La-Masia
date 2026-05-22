from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT_DIR = Path(__file__).resolve().parents[1]
MAPPING_PATH = ROOT_DIR / "data" / "team_id_mapping.json"
MANUAL_LOGOS_PATH = ROOT_DIR / "data" / "manual_logos.json"

_api_mapping_cache: dict[str, int] | None = None
_external_mapping_cache: dict[str, str] | None = None
_mapping_mtime: float | None = None
_manual_mapping_cache: dict[str, str] | None = None
_manual_mapping_mtime: float | None = None


def get_api_football_id(sofascore_team_id: int | str | None) -> int | None:
    sofascore_id = _normalize_id(sofascore_team_id)
    if sofascore_id is None:
        return None

    mapping = _load_mapping()
    value = mapping.get(str(sofascore_id))
    return value if isinstance(value, int) and value > 0 else None


def get_external_logo_path(sofascore_team_id: int | str | None) -> Path | None:
    sofascore_id = _normalize_id(sofascore_team_id)
    if sofascore_id is None:
        return None

    _load_mapping()
    if _external_mapping_cache is None:
        return None
    relative_path = _external_mapping_cache.get(str(sofascore_id))
    if not relative_path:
        return None
    path = ROOT_DIR / relative_path
    return path if path.exists() and path.stat().st_size > 0 else None


def get_manual_logo_path(sofascore_team_id: int | str | None) -> Path | None:
    sofascore_id = _normalize_id(sofascore_team_id)
    if sofascore_id is None:
        return None

    mapping = _load_manual_mapping()
    relative_path = mapping.get(str(sofascore_id))
    if not relative_path:
        return None
    path = ROOT_DIR / relative_path
    return path if path.exists() and path.stat().st_size > 0 else None


def _load_mapping() -> dict[str, int]:
    global _api_mapping_cache, _external_mapping_cache, _mapping_mtime

    try:
        mtime = MAPPING_PATH.stat().st_mtime
    except OSError:
        _api_mapping_cache = {}
        _external_mapping_cache = {}
        _mapping_mtime = None
        return {}

    if _api_mapping_cache is not None and _external_mapping_cache is not None and _mapping_mtime == mtime:
        return _api_mapping_cache

    try:
        payload = json.loads(MAPPING_PATH.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        _api_mapping_cache = {}
        _external_mapping_cache = {}
        _mapping_mtime = mtime
        return {}

    raw_mapping: Any = payload.get("sofascore_to_api_football") if isinstance(payload, dict) else {}
    if not isinstance(raw_mapping, dict):
        raw_mapping = {}
    raw_external: Any = payload.get("sofascore_to_external_logo") if isinstance(payload, dict) else {}
    if not isinstance(raw_external, dict):
        raw_external = {}

    parsed: dict[str, int] = {}
    for key, value in raw_mapping.items():
        sofascore_id = _normalize_id(key)
        api_football_id = _normalize_id(value)
        if sofascore_id is None or api_football_id is None:
            continue
        parsed[str(sofascore_id)] = api_football_id

    external: dict[str, str] = {}
    for key, value in raw_external.items():
        sofascore_id = _normalize_id(key)
        if sofascore_id is None or not isinstance(value, str) or not value:
            continue
        external[str(sofascore_id)] = value

    _api_mapping_cache = parsed
    _external_mapping_cache = external
    _mapping_mtime = mtime
    return parsed


def _load_manual_mapping() -> dict[str, str]:
    global _manual_mapping_cache, _manual_mapping_mtime

    try:
        mtime = MANUAL_LOGOS_PATH.stat().st_mtime
    except OSError:
        _manual_mapping_cache = {}
        _manual_mapping_mtime = None
        return {}

    if _manual_mapping_cache is not None and _manual_mapping_mtime == mtime:
        return _manual_mapping_cache

    try:
        payload = json.loads(MANUAL_LOGOS_PATH.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        _manual_mapping_cache = {}
        _manual_mapping_mtime = mtime
        return {}

    raw_mapping: Any = payload.get("sofascore_to_manual_logo") if isinstance(payload, dict) else {}
    if not isinstance(raw_mapping, dict):
        raw_mapping = {}

    parsed: dict[str, str] = {}
    for key, value in raw_mapping.items():
        sofascore_id = _normalize_id(key)
        if sofascore_id is None or not isinstance(value, str) or not value:
            continue
        parsed[str(sofascore_id)] = value

    _manual_mapping_cache = parsed
    _manual_mapping_mtime = mtime
    return parsed


def _normalize_id(value: int | str | None) -> int | None:
    if value is None:
        return None
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return None
    return parsed if parsed > 0 else None
