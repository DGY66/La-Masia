from __future__ import annotations

from io import BytesIO
from pathlib import Path
from urllib.request import Request, urlopen

import customtkinter as ctk

from team_id_mapping import get_external_logo_path, get_manual_logo_path


ESPN_LOGO_DIR = Path(__file__).resolve().parent / "assets" / "espn_logos"
TRANSFERMARKT_LOGO_DIR = Path(__file__).resolve().parent / "assets" / "logos"
ESPN_LOGO_URL = "https://a.espncdn.com/i/teamlogos/soccer/500/{team_id}.png"
TRANSFERMARKT_LOGO_URL = "https://raw.githubusercontent.com/luukhopman/football-logos/master/logos/{team_id}.png"
REMOTE_HEADERS = {
    "user-agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/136.0.0.0 Safari/537.36"
    ),
    "accept": "image/png,image/*;q=0.8,*/*;q=0.5",
}

_pil_cache: dict[tuple[str, tuple[int, int]], object] = {}
_placeholder_pil_cache: dict[tuple[int, int], object] = {}


def get_best_team_logo(team: object, size: tuple[int, int] = (32, 32)) -> ctk.CTkImage:
    manual_path = get_manual_logo_path(_get_team_value(team, "team_id"))
    if manual_path is not None:
        return _load_local_logo(manual_path, size)

    external_path = get_external_logo_path(_get_team_value(team, "team_id"))
    if external_path is not None:
        return _load_local_logo(external_path, size)

    logo_url = _get_team_value(team, "team_logo_url")
    if isinstance(logo_url, str) and logo_url:
        image = _try_load_logo(logo_url, size)
        if image is not None:
            return image

    espn_id = _get_team_value(team, "espn_id")
    espn_path = _local_logo_path(ESPN_LOGO_DIR, espn_id)
    if espn_path is not None:
        return _load_local_logo(espn_path, size)

    transfermarkt_id = _get_team_value(team, "transfermarkt_id")
    transfermarkt_path = _local_logo_path(TRANSFERMARKT_LOGO_DIR, transfermarkt_id)
    if transfermarkt_path is not None:
        return _load_local_logo(transfermarkt_path, size)

    espn_remote = _remote_logo_url(ESPN_LOGO_URL, espn_id)
    if espn_remote is not None:
        image = _try_load_logo(espn_remote, size)
        if image is not None:
            return image

    transfermarkt_remote = _remote_logo_url(TRANSFERMARKT_LOGO_URL, transfermarkt_id)
    if transfermarkt_remote is not None:
        image = _try_load_logo(transfermarkt_remote, size)
        if image is not None:
            return image

    return _get_placeholder(size)


def _get_team_value(team: object, key: str) -> int | str | None:
    if isinstance(team, dict):
        value = team.get(key)
    else:
        value = getattr(team, key, None)
    return value if isinstance(value, (int, str)) else None


def _local_logo_path(directory: Path, team_id: int | str | None) -> Path | None:
    parsed_id = _parse_team_id(team_id)
    if parsed_id is None:
        return None
    path = directory / f"{parsed_id}.png"
    return path if path.exists() and path.stat().st_size > 0 else None


def _remote_logo_url(template: str, team_id: int | str | None) -> str | None:
    parsed_id = _parse_team_id(team_id)
    if parsed_id is None:
        return None
    return template.format(team_id=parsed_id)


def _try_load_logo(source: str, size: tuple[int, int]) -> ctk.CTkImage | None:
    try:
        return _load_remote_logo(source, size)
    except Exception:
        return None


def _load_remote_logo(url: str, size: tuple[int, int]) -> ctk.CTkImage:
    image = _load_pil_image(url, size)
    return ctk.CTkImage(light_image=image, dark_image=image, size=size)


def _load_local_logo(path: Path, size: tuple[int, int]) -> ctk.CTkImage:
    image = _load_pil_image(str(path.resolve()), size)
    return ctk.CTkImage(light_image=image, dark_image=image, size=size)


def _load_pil_image(source: str, size: tuple[int, int]):
    cache_key = (source, size)
    cached = _pil_cache.get(cache_key)
    if cached is not None:
        return cached.copy()

    image_lib = _require_pillow()
    if source.startswith(("http://", "https://")):
        from urllib.error import HTTPError
        import subprocess

        try:
            request = Request(source, headers=REMOTE_HEADERS)
            with urlopen(request, timeout=4) as response:
                data = response.read()
        except HTTPError as exc:
            if exc.code != 403:
                raise
            command = ["curl.exe", "-s", "-L", "--max-time", "10"]
            for key, value in REMOTE_HEADERS.items():
                command.extend(["-H", f"{key}: {value}"])
            command.append(source)
            result = subprocess.run(command, capture_output=True, check=False)
            if result.returncode != 0:
                stderr = result.stderr.decode("utf-8", errors="ignore").strip()
                raise OSError(stderr or f"curl failed with exit code {result.returncode}")
            if not result.stdout:
                raise OSError("empty image response")
            data = result.stdout
        image = image_lib.open(BytesIO(data)).convert("RGBA")
    else:
        image = image_lib.open(source).convert("RGBA")

    image = image.resize(size, image_lib.Resampling.LANCZOS)
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
        raise RuntimeError("Pillow is required for logo loading") from exc
    return Image
