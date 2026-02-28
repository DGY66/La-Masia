from typing import Final

TEAMS_DATA: Final[list[tuple[str, str]]] = [
    ("AR", "Arsenal Fc"),
    ("BM", "Bayern München"),
    ("LP", "Liverpool"),
    ("TH", "Tottenham"),
    ("BL", "Barcelona"),
    ("CH", "Chelsea"),
    ("SP", "Sporting CP"),
    ("MC", "Manchester City"),
    ("RM", "Real Madrid"),
    ("IN", "Inter"),
    ("PS", "Paris"),
    ("NC", "Newcastle"),
    ("JU", "Juventus"),
    ("AL", "Atletico"),
    ("AT", "Atalanta"),
    ("LK", "Leverkusen"),
    ("DM", "B.Dortmund"),
    ("OM", "Olympiacos"),
    ("CB", "Club Brugge"),
    ("GL", "Galatasaray"),
    ("MO", "Monaco"),
    ("QA", "Qarabağ"),
    ("BO", "Bodo/Glimt"),
    ("BE", "Benfica"),
    ("MA", "Marseille"),
    ("PA", "Pafos"),
    ("UN", "Union SG"),
    ("PV", "PSV"),
    ("AC", "Athletic Club"),
    ("NA", "Napoli"),
    ("CO", "Copenhagen"),
    ("AJ", "Ajax"),
    ("FR", "Frankfurt"),
    ("SL", "Slavia Praha"),
    ("VL", "Villareal"),
    ("KA", "Kairat Almaty"),
]

SECTIONS: Final[list[tuple[int, int, str, str]]] = [
    (0, 8, "Straight to R16", "r16"),
    (8, 16, "Knockout phase play-off places (Seeded)", "seeded"),
    (16, 24, "Knockout phase play-off places (Unseeded)", "unseeded"),
    (24, 36, "Elimination places", "elim"),
]

COL_HEADERS: Final[list[str]] = [
    "#", "CLUB", "", "PLD", "W", "D", "L", "For", "GA", "GD", "PTS", "FORM",
]

COL_WIDTHS: Final[list[int]] = [40, 50, 130, 45, 35, 35, 35, 40, 40, 40, 45, 160]

ZONE_COLORS: Final[dict[str, str]] = {
    "r16": "#1B8A2F",
    "seeded": "#1565C0",
    "unseeded": "#E65100",
    "elim": "#C62828",
}

FORM_WIN: Final[str] = "#4CAF50"
FORM_DRAW: Final[str] = "#9E9E9E"
FORM_LOSS: Final[str] = "#F44336"

HEADER_BG: Final[str] = "#0D1B5E"
CARD_BG: Final[str] = "#1E1E2E"
ROW_BG: Final[str] = "#1E1E2E"
ROW_ALT_BG: Final[str] = "#232336"
SECTION_BG: Final[str] = "#2A2A3D"
TEXT_COLOR: Final[str] = "#EAEAEA"
SUBTEXT_COLOR: Final[str] = "#AAAAAA"
BADGE_BG: Final[str] = "#1565C0"
APP_BG: Final[str] = "#0A0A1A"
OUTER_BG: Final[str] = "#12121F"
SEPARATOR_COLOR: Final[str] = "#444466"
SCROLLBAR_COLOR: Final[str] = "#444466"
SCROLLBAR_HOVER: Final[str] = "#5555AA"
LINK_COLOR: Final[str] = "#6688CC"
SUBTITLE_COLOR: Final[str] = "#AABBDD"

RAPIDAPI_HOST: Final[str] = "sportapi7.p.rapidapi.com"
RAPIDAPI_BASE_URL: Final[str] = f"https://{RAPIDAPI_HOST}/api/v1"
REQUEST_TIMEOUT: Final[int] = 10

# SofaScore season IDs for UCL
# 2024/25 season: 61644
# 2025/26 season: 65360 (may return 404 if season not started yet)
#
# Note: The season ID 65360 for 2025/26 may not be active until the actual
# tournament starts (typically September 2025). Until then, the API returns 404.
# The app automatically falls back to the 2024/25 season (61644) with a clear
# warning displayed in the UI.
UCL_SEASON_ID: Final[int] = 65360  # Target season (2025/26)
UCL_FALLBACK_SEASON_ID: Final[int] = 61644  # Fallback to 2024/25 if 2025/26 not available