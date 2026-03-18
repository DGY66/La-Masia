from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Final


@dataclass(frozen=True)
class CompetitionConfig:
    key: str
    title: str
    short_title: str
    season_label: str
    archive_season_label: str
    mock_season_label: str
    tournament_id: int
    preferred_season_id: int | None
    fallback_season_id: int | None
    header_gradient: tuple[str, str]
    footer_gradient: tuple[str, str]
    badge_gradient: tuple[str, str]
    app_title: str
    logo_lines: tuple[str, ...]
    logo_path: str
    matchday_text: str
    nav_targets: tuple[str, str]


ASSETS_DIR: Final[Path] = Path(__file__).parent / "assets"


SECTIONS: Final[list[tuple[int, int, str, str]]] = [
    (0, 8, "Straight to R16", "r16"),
    (8, 16, "Knockout phase play-off places (Seeded)", "seeded"),
    (16, 24, "Knockout phase play-off places (Unseeded)", "unseeded"),
    (24, 36, "Elimination places", "elim"),
]

VISIBLE_SECTIONS: Final[int] = 2
VISIBLE_TEAMS: Final[int] = 16

COL_HEADERS: Final[list[str]] = [
    "#", "CLUB", "", "PLD", "W", "D", "L", "For", "GA", "GD", "PTS", "FORM",
]

COL_WIDTHS: Final[list[int]] = [44, 58, 420, 52, 44, 44, 44, 50, 50, 50, 54, 320]

ZONE_COLORS: Final[dict[str, str]] = {
    "r16": "#00D628",
    "seeded": "#00D628",
    "unseeded": "#00D628",
    "elim": "#00D628",
}

FORM_WIN: Final[str] = "#48F15A"
FORM_DRAW: Final[str] = "#A6B9AB"
FORM_LOSS: Final[str] = "#FF4B4B"

APP_BG: Final[str] = "#FFFFFF"
OUTER_BG: Final[str] = "#FFFFFF"
CARD_BG: Final[str] = "#F3F7FC"
CARD_SHADOW: Final[str] = "#E9EEF7"
ROW_BG: Final[str] = "#F3F7FC"
ROW_ALT_BG: Final[str] = "#F3F7FC"
SECTION_BG: Final[str] = "#EDF2F8"
TEXT_COLOR: Final[str] = "#111111"
SUBTEXT_COLOR: Final[str] = "#6F6F6F"
MUTED_TEXT: Final[str] = "#D9D9D9"
LINK_COLOR: Final[str] = "#000000"
SCROLLBAR_COLOR: Final[str] = "#B7C2D6"
SCROLLBAR_HOVER: Final[str] = "#93A4C4"
SEPARATOR_COLOR: Final[str] = "#606060"
CARD_BORDER: Final[str] = "#E8EDF5"

RAPIDAPI_HOST: Final[str] = "sportapi7.p.rapidapi.com"
RAPIDAPI_BASE_URL: Final[str] = f"https://{RAPIDAPI_HOST}/api/v1"
REQUEST_TIMEOUT: Final[int] = 10

UCL_SEASON_ID: Final[int | None] = None
UCL_FALLBACK_SEASON_ID: Final[int | None] = None
UEL_SEASON_ID: Final[int | None] = None
UEL_FALLBACK_SEASON_ID: Final[int | None] = None
UECL_SEASON_ID: Final[int | None] = None
UECL_FALLBACK_SEASON_ID: Final[int | None] = None

UCL_COMPETITION: Final[CompetitionConfig] = CompetitionConfig(
    key="ucl",
    title="UEFA Champions League",
    short_title="UCL",
    season_label="League Phase 2025/26",
    archive_season_label="League Phase 2024/25 (Archive)",
    mock_season_label="League Phase 2025/26 (Mock Data - API Unavailable)",
    tournament_id=7,
    preferred_season_id=UCL_SEASON_ID,
    fallback_season_id=UCL_FALLBACK_SEASON_ID,
    header_gradient=("#0015B4", "#00094E"),
    footer_gradient=("#0015B4", "#00094E"),
    badge_gradient=("#092183", "#103BE9"),
    app_title="UEFA Champions League",
    logo_lines=("UEFA", "CHAMPIONS", "LEAGUE"),
    logo_path=str(ASSETS_DIR / "img.png"),
    matchday_text="Matchday 8 of 8",
    nav_targets=("uel", "uecl"),
)

UEL_COMPETITION: Final[CompetitionConfig] = CompetitionConfig(
    key="uel",
    title="UEFA Europe League",
    short_title="UEL",
    season_label="League Phase 2025/26",
    archive_season_label="League Phase (Archive)",
    mock_season_label="League Phase 2025/26 (Mock Data - API Unavailable)",
    tournament_id=679,
    preferred_season_id=UEL_SEASON_ID,
    fallback_season_id=UEL_FALLBACK_SEASON_ID,
    header_gradient=("#D45917", "#110E0C"),
    footer_gradient=("#D45917", "#110E0C"),
    badge_gradient=("#030C2F", "#E97C10"),
    app_title="UEFA Europe League",
    logo_lines=("UEFA", "EUROPA", "LEAGUE"),
    logo_path=str(ASSETS_DIR / "img_1.png"),
    matchday_text="Matchday 8 of 8",
    nav_targets=("ucl", "uecl"),
)

UECL_COMPETITION: Final[CompetitionConfig] = CompetitionConfig(
    key="uecl",
    title="UEFA Conference League",
    short_title="UECL",
    season_label="League Phase 2025/26",
    archive_season_label="League Phase (Archive)",
    mock_season_label="League Phase 2025/26 (Mock Data - API Unavailable)",
    tournament_id=17015,
    preferred_season_id=UECL_SEASON_ID,
    fallback_season_id=UECL_FALLBACK_SEASON_ID,
    header_gradient=("#0ACB1A", "#062E07"),
    footer_gradient=("#0ACB1A", "#062E07"),
    badge_gradient=("#11FF45", "#25190E"),
    app_title="UEFA Conference League",
    logo_lines=("UEFA", "EUROPA CONFERENCE", "LEAGUE"),
    logo_path=str(ASSETS_DIR / "img_2.png"),
    matchday_text="Matchday 8 of 8",
    nav_targets=("ucl", "uel"),
)

COMPETITIONS: Final[dict[str, CompetitionConfig]] = {
    "ucl": UCL_COMPETITION,
    "uel": UEL_COMPETITION,
    "uecl": UECL_COMPETITION,
}
