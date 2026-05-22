from __future__ import annotations

from pathlib import Path

import customtkinter as ctk

from team_id_mapping import get_api_football_id, get_external_logo_path, get_manual_logo_path


ROOT_DIR = Path(__file__).resolve().parents[1]
TEAM_LOGO_DIR = ROOT_DIR / "assets" / "logos" / "teams"
ESPN_LOGO_DIR = Path(__file__).resolve().parent / "assets" / "espn_logos"
TRANSFERMARKT_LOGO_DIR = Path(__file__).resolve().parent / "assets" / "logos"


_pil_cache: dict[tuple[str, tuple[int, int]], object] = {}
_placeholder_pil_cache: dict[tuple[int, int], object] = {}


def get_team_logo(team_id: int | str | None, size: tuple[int, int] = (32, 32)) -> ctk.CTkImage:
    parsed_id = _parse_team_id(team_id)
    if parsed_id is None:
        return _get_placeholder(size)

    path = TEAM_LOGO_DIR / f"{parsed_id}.png"
    if not path.exists() or path.stat().st_size == 0:
        return _get_placeholder(size)

    try:
        image = _load_pil_image(path, size)
    except Exception:
        return _get_placeholder(size)

    return ctk.CTkImage(light_image=image, dark_image=image, size=size)


def has_team_logo(team_id: int | str | None) -> bool:
    parsed_id = _parse_team_id(team_id)
    if parsed_id is None:
        return False
    path = TEAM_LOGO_DIR / f"{parsed_id}.png"
    return path.exists() and path.stat().st_size > 0


def get_best_team_logo(team: object, size: tuple[int, int] = (32, 32)) -> ctk.CTkImage:
    api_football_id = _get_team_value(team, "api_football_id")
    if api_football_id is None:
        api_football_id = get_api_football_id(_get_team_value(team, "team_id"))
    if has_team_logo(api_football_id):
        return get_team_logo(api_football_id, size)

    external_path = get_external_logo_path(_get_team_value(team, "team_id"))
    if external_path is not None:
        return _load_local_logo(external_path, size)

    manual_path = get_manual_logo_path(_get_team_value(team, "team_id"))
    if manual_path is not None:
        return _load_local_logo(manual_path, size)

    espn_id = _get_team_value(team, "espn_id")
    espn_path = _local_logo_path(ESPN_LOGO_DIR, espn_id)
    if espn_path is not None:
        return _load_local_logo(espn_path, size)

    transfermarkt_id = _get_team_value(team, "transfermarkt_id")
    transfermarkt_path = _local_logo_path(TRANSFERMARKT_LOGO_DIR, transfermarkt_id)
    if transfermarkt_path is not None:
        return _load_local_logo(transfermarkt_path, size)

    return _get_placeholder(size)


def clear_team_logo_cache() -> None:
    _pil_cache.clear()
    _placeholder_pil_cache.clear()


def _get_team_value(team: object, key: str) -> int | str | None:
    if isinstance(team, dict):
        value = team.get(key)
    else:
        value = getattr(team, key, None)
    if value is None:
        return None
    return value if isinstance(value, (int, str)) else None


def _local_logo_path(directory: Path, team_id: int | str | None) -> Path | None:
    parsed_id = _parse_team_id(team_id)
    if parsed_id is None:
        return None
    path = directory / f"{parsed_id}.png"
    return path if path.exists() and path.stat().st_size > 0 else None


def _load_local_logo(path: Path, size: tuple[int, int]) -> ctk.CTkImage:
    image = _load_pil_image(path, size)
    return ctk.CTkImage(light_image=image, dark_image=image, size=size)


def _load_pil_image(path: Path, size: tuple[int, int]):
    cache_key = (str(path.resolve()), size)
    cached = _pil_cache.get(cache_key)
    if cached is not None:
        return cached.copy()

    image_lib = _require_pillow()
    image = image_lib.open(path).convert("RGBA").resize(size, image_lib.Resampling.LANCZOS)
    _pil_cache[cache_key] = image.copy()
    return image


def _parse_team_id(team_id: int | str | None) -> int | None:
    if team_id is None:
        return None
    try:
        parsed = int(team_id)
    except (TypeError, ValueError):
        return None
    return parsed if parsed > 0 else None


def _get_placeholder(size: tuple[int, int]) -> ctk.CTkImage:
    image_lib = _require_pillow()
    cached = _placeholder_pil_cache.get(size)
    image = cached.copy() if cached is not None else image_lib.new("RGBA", size, (48, 58, 92, 255))
    if cached is None:
        _placeholder_pil_cache[size] = image.copy()
    return ctk.CTkImage(light_image=image, dark_image=image, size=size)


def _require_pillow():
    try:
        from PIL import Image
    except ModuleNotFoundError as exc:
        raise RuntimeError("Pillow is required for CTkImage logo loading") from exc
    return Image
