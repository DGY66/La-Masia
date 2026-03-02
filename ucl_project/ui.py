from __future__ import annotations

import customtkinter as ctk

from models import Team
from config import (
    TEAMS_DATA, SECTIONS, COL_HEADERS, COL_WIDTHS,
    ZONE_COLORS, FORM_WIN, FORM_DRAW, FORM_LOSS,
    HEADER_BG, CARD_BG, ROW_BG, ROW_ALT_BG,
    SECTION_BG, TEXT_COLOR, SUBTEXT_COLOR, BADGE_BG,
    APP_BG, OUTER_BG, SEPARATOR_COLOR,
    SCROLLBAR_COLOR, SCROLLBAR_HOVER,
    LINK_COLOR, SUBTITLE_COLOR, UCL_SEASON_ID, UCL_FALLBACK_SEASON_ID,
)

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class UCLTableApp(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()
        self.title("UEFA Champions League")
        self.geometry("1300x830")
        self.resizable(True, True)
        self.configure(fg_color=APP_BG)

        self.teams: list[Team] = [Team(abbr, name) for abbr, name in TEAMS_DATA]
        self.last_update: str = "Never"
        self.is_fallback_data: bool = False

        self._build_header()
        self._build_table_area()
        self._render_table()

        # Auto-refresh from API on startup
        self.after(100, self.refresh_from_api)

    def set_teams(self, teams: list[Team], last_update: str | None = None, is_fallback: bool = False) -> None:
        self.teams = teams
        self.is_fallback_data = is_fallback
        if last_update:
            self.last_update = last_update
        self._update_header_timestamp()
        self._update_season_label()
        self._render_table()

    def refresh_from_api(self) -> None:
        """Fetch latest standings from SofaScore API with fallback support"""
        try:
            from api import UCLApiClient, ApiError
            import logging

            logging.basicConfig(level=logging.INFO)
            logger = logging.getLogger(__name__)

            logger.info(f"Fetching UCL standings for season {UCL_SEASON_ID} (2025/26)...")
            client = UCLApiClient()

            # Try 2025/26 season with 2024/25 fallback
            teams, last_update, is_fallback = client.get_standings(
                season=UCL_SEASON_ID,
                fallback_season=UCL_FALLBACK_SEASON_ID
            )

            if teams:
                self.set_teams(teams, last_update, is_fallback)
                if is_fallback:
                    logger.warning(f"⚠️  Displaying {len(teams)} teams from archived 24/25 season")
                else:
                    logger.info(f"Successfully loaded {len(teams)} teams from 25/26 season")
            else:
                logger.warning("API returned empty teams list")
                self._show_error_message("No data available")

        except Exception as exc:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to fetch API data: {exc}")
            print(f"[API ERROR] {exc}")

            # If API completely fails (rate limit or any error), use mock data
            logger.warning("⚠️  API unavailable - loading mock data")
            self._load_mock_data()

    def _load_mock_data(self) -> None:
        """Load mock data when API is unavailable"""
        try:
            from mock_data import get_mock_teams
            from datetime import datetime

            teams = get_mock_teams()
            timestamp = f"Mock Data (API rate limited)"
            self.set_teams(teams, timestamp, is_fallback=True)

            # Update season label to show it's mock data
            if hasattr(self, 'season_label'):
                self.season_label.configure(
                    text="League Phase 2024/25 (Mock Data - API Rate Limited)",
                    text_color="#FF5722"  # Deep orange for mock data warning
                )

            print(f"[INFO] Loaded {len(teams)} teams from mock data")
            print("[INFO] Wait 1 hour or use different API key to refresh real data")

        except Exception as e:
            print(f"[ERROR] Failed to load mock data: {e}")
            self._show_error_message("No data available")

    def _show_error_message(self, message: str) -> None:
        """Display error message in the UI"""
        self.last_update = f"Error: {message}"
        self._update_header_timestamp()

    def _build_header(self) -> None:
        self.header = ctk.CTkFrame(self, fg_color=HEADER_BG, corner_radius=0, height=110)
        self.header.pack(fill="x", side="top")
        self.header.pack_propagate(False)

        left = ctk.CTkFrame(self.header, fg_color="transparent")
        left.place(x=30, y=18)
        ctk.CTkLabel(
            left, text="UEFA Champions League",
            font=ctk.CTkFont(family="Arial", size=24, weight="bold"),
            text_color="white",
        ).pack(anchor="w")
        self.season_label = ctk.CTkLabel(
            left, text="League Phase 2025/26",
            font=ctk.CTkFont(family="Arial", size=13),
            text_color=SUBTITLE_COLOR,
        )
        self.season_label.pack(anchor="w", pady=(2, 0))

        right = ctk.CTkFrame(self.header, fg_color="transparent")
        right.place(relx=1.0, x=-30, y=18, anchor="ne")
        ctk.CTkLabel(
            right, text="Matchday 8 of 8",
            font=ctk.CTkFont(family="Arial", size=13, weight="bold"),
            text_color="white",
        ).pack(anchor="e")
        self.timestamp_label = ctk.CTkLabel(
            right, text=f"Last updated: {self.last_update}",
            font=ctk.CTkFont(family="Arial", size=11),
            text_color=SUBTITLE_COLOR,
        )
        self.timestamp_label.pack(anchor="e", pady=(2, 0))

        ctk.CTkButton(
            self.header, text="Go to UEL",
            font=ctk.CTkFont(size=13),
            fg_color="white", text_color=HEADER_BG,
            hover_color="#DDDDDD",
            corner_radius=20, width=130, height=32,
        ).place(relx=0.5, y=12, anchor="n")

    def _update_header_timestamp(self) -> None:
        """Update the timestamp label in the header"""
        if hasattr(self, 'timestamp_label'):
            self.timestamp_label.configure(text=f"Last updated: {self.last_update}")

    def _update_season_label(self) -> None:
        """Update the season label to show archive warning if fallback is used"""
        if hasattr(self, 'season_label'):
            if self.is_fallback_data:
                self.season_label.configure(
                    text="League Phase 2024/25 (Archive) - 25/26 not available",
                    text_color="#FF9800"  # Orange warning color
                )
            else:
                self.season_label.configure(
                    text="League Phase 2025/26",
                    text_color=SUBTITLE_COLOR
                )

    def _build_table_area(self) -> None:
        self.outer = ctk.CTkFrame(self, fg_color=OUTER_BG, corner_radius=0)
        self.outer.pack(fill="both", expand=True, padx=0, pady=0)

        self.scroll = ctk.CTkScrollableFrame(
            self.outer,
            fg_color=CARD_BG,
            corner_radius=14,
            scrollbar_button_color=SCROLLBAR_COLOR,
            scrollbar_button_hover_color=SCROLLBAR_HOVER,
        )
        self.scroll.pack(fill="both", expand=True, padx=28, pady=(16, 10))

    def _render_table(self) -> None:
        for w in self.scroll.winfo_children():
            w.destroy()

        sorted_teams = sorted(self.teams, key=lambda t: t.sort_key())

        self._render_header_row()

        row_idx = 1
        for sec_start, sec_end, sec_label, sec_key in SECTIONS:
            row_idx = self._render_section_header(row_idx, sec_label, sec_key)
            for pos_in_section, team in enumerate(sorted_teams[sec_start:sec_end]):
                global_pos = sec_start + pos_in_section + 1
                is_alt = pos_in_section % 2 == 1
                row_idx = self._render_team_row(row_idx, global_pos, team, sec_key, is_alt)

        self._render_footer(row_idx)

    def _render_header_row(self) -> None:
        hdr = ctk.CTkFrame(self.scroll, fg_color="transparent", height=36)
        hdr.grid(row=0, column=0, sticky="ew", padx=0, pady=(6, 0))
        self.scroll.grid_columnconfigure(0, weight=1)
        hdr.grid_columnconfigure(list(range(len(COL_HEADERS))), weight=0)
        hdr.grid_columnconfigure(2, weight=1)

        for c, (txt, w) in enumerate(zip(COL_HEADERS, COL_WIDTHS)):
            if c in (2, 11):
                anchor = "w"
            elif c <= 1:
                anchor = "center"
            else:
                anchor = "center"
            ctk.CTkLabel(
                hdr, text=txt, width=w,
                font=ctk.CTkFont(family="Arial", size=12, weight="bold"),
                text_color=SUBTEXT_COLOR, anchor=anchor,
            ).grid(row=0, column=c, padx=(2, 2), pady=4, sticky="ew" if c == 2 else "")

        ctk.CTkFrame(self.scroll, height=2, fg_color=SEPARATOR_COLOR).grid(
            row=1, column=0, sticky="ew", padx=8, pady=(0, 2),
        )

    def _render_section_header(self, row_idx: int, label: str, zone_key: str) -> int:
        zone_color = ZONE_COLORS[zone_key]

        ctk.CTkFrame(self.scroll, height=3, fg_color=zone_color).grid(
            row=row_idx, column=0, sticky="ew", padx=8, pady=(8, 0),
        )
        row_idx += 1

        sec_frame = ctk.CTkFrame(self.scroll, fg_color=SECTION_BG, height=30, corner_radius=0)
        sec_frame.grid(row=row_idx, column=0, sticky="ew", padx=8, pady=(0, 2))

        ctk.CTkFrame(sec_frame, width=4, fg_color=zone_color, corner_radius=0).place(
            x=0, y=0, relheight=1.0,
        )
        ctk.CTkLabel(
            sec_frame, text=f"  {label}",
            font=ctk.CTkFont(family="Arial", size=11, weight="bold"),
            text_color=SUBTEXT_COLOR, anchor="w",
        ).pack(side="left", padx=(10, 0), pady=4)

        row_idx += 1
        return row_idx

    def _render_team_row(
        self, row_idx: int, pos: int, team: Team, zone_key: str, is_alt: bool,
    ) -> int:
        zone_color = ZONE_COLORS[zone_key]
        bg = ROW_ALT_BG if is_alt else ROW_BG

        row_frame = ctk.CTkFrame(self.scroll, fg_color=bg, height=38, corner_radius=0)
        row_frame.grid(row=row_idx, column=0, sticky="ew", padx=8, pady=0)
        row_frame.grid_propagate(False)

        ctk.CTkFrame(row_frame, width=4, fg_color=zone_color, corner_radius=0).place(
            x=0, y=0, relheight=1.0,
        )

        # Configure column weights (only team name column should expand)
        for c in range(len(COL_HEADERS)):
            row_frame.grid_columnconfigure(c, weight=(1 if c == 2 else 0), minsize=COL_WIDTHS[c])

        # Column 0: Position
        ctk.CTkLabel(
            row_frame, text=str(pos), width=COL_WIDTHS[0],
            font=ctk.CTkFont(family="Arial", size=12, weight="bold"),
            text_color=TEXT_COLOR, anchor="center",
        ).grid(row=0, column=0, padx=(8, 2), pady=6)

        # Column 1: Badge
        self._render_badge(row_frame, team, col=1)

        # Column 2: Team Name
        ctk.CTkLabel(
            row_frame, text=team.name, width=COL_WIDTHS[2],
            font=ctk.CTkFont(family="Arial", size=12, weight="normal"),
            text_color=TEXT_COLOR, anchor="w",
        ).grid(row=0, column=2, padx=(2, 2), pady=6, sticky="ew")

        # Columns 3-10: Stats
        stats = [
            str(team.pld), str(team.w), str(team.d), str(team.l),
            str(team.gf), str(team.ga), str(team.gd), str(team.pts)
        ]
        for idx, (stat, col_idx) in enumerate(zip(stats, range(3, 11))):
            font_w = "bold" if col_idx == 10 else "normal"
            text_clr = "white" if col_idx == 10 else TEXT_COLOR
            ctk.CTkLabel(
                row_frame, text=stat, width=COL_WIDTHS[col_idx],
                font=ctk.CTkFont(family="Arial", size=12, weight=font_w),
                text_color=text_clr, anchor="center",
            ).grid(row=0, column=col_idx, padx=(2, 2), pady=6)

        # Column 11: Form
        self._render_form(row_frame, team, col=11)

        return row_idx + 1

    @staticmethod
    def _render_badge(parent: ctk.CTkFrame, team: Team, col: int) -> None:
        badge = ctk.CTkFrame(parent, width=34, height=24, fg_color=BADGE_BG, corner_radius=6)
        badge.grid(row=0, column=col, padx=(4, 4), pady=6)
        badge.grid_propagate(False)
        ctk.CTkLabel(
            badge, text=team.abbr,
            font=ctk.CTkFont(family="Arial", size=10, weight="bold"),
            text_color="white",
        ).place(relx=0.5, rely=0.5, anchor="center")

    @staticmethod
    def _render_form(parent: ctk.CTkFrame, team: Team, col: int) -> None:
        """Render form indicators as colored dots"""
        form_frame = ctk.CTkFrame(parent, fg_color="transparent", height=24, width=COL_WIDTHS[col])
        form_frame.grid(row=0, column=col, padx=(4, 8), pady=6, sticky="w")
        form_frame.grid_propagate(False)

        # If no form data, show empty
        if not team.form:
            ctk.CTkLabel(
                form_frame, text="-",
                font=ctk.CTkFont(family="Arial", size=12),
                text_color=SUBTEXT_COLOR,
            ).pack(side="left", padx=2)
            return

        # Render colored dots for each match result
        for fi, f in enumerate(team.form):
            clr = FORM_WIN if f == "W" else (FORM_LOSS if f == "L" else FORM_DRAW)
            dot = ctk.CTkFrame(form_frame, width=16, height=16, fg_color=clr, corner_radius=8)
            dot.grid(row=0, column=fi, padx=2)
            dot.grid_propagate(False)

    def _render_footer(self, row_idx: int) -> None:
        ctk.CTkFrame(self.scroll, fg_color="transparent", height=10).grid(
            row=row_idx, column=0, sticky="ew",
        )
        row_idx += 1

        legend = ctk.CTkFrame(self.scroll, fg_color="transparent")
        legend.grid(row=row_idx, column=0, sticky="w", padx=16, pady=(4, 2))
        ctk.CTkFrame(
            legend, width=12, height=12, fg_color=ZONE_COLORS["r16"], corner_radius=6,
        ).grid(row=0, column=0, padx=(0, 6))
        ctk.CTkLabel(
            legend, text="Qualified",
            font=ctk.CTkFont(size=11, weight="bold"), text_color=TEXT_COLOR,
        ).grid(row=0, column=1)
        row_idx += 1

        ctk.CTkLabel(
            self.scroll,
            text="Want to learn more about the format? Check the competition regulations",
            font=ctk.CTkFont(size=11), text_color=LINK_COLOR, anchor="w", cursor="hand2",
        ).grid(row=row_idx, column=0, sticky="w", padx=16, pady=(0, 4))
        row_idx += 1

        ctk.CTkLabel(
            self.scroll,
            text=(
                "Standings are provisional until all league phase matches have been played and officially "
                "validated by UEFA. Confirmations of qualification / elimination are based on the provisional "
                "standings and are therefore for guidance purposes only until all league phase matches are "
                "completed and final standings have been validated by UEFA."
            ),
            font=ctk.CTkFont(size=10), text_color=SUBTEXT_COLOR,
            anchor="w", justify="left", wraplength=1100,
        ).grid(row=row_idx, column=0, sticky="w", padx=16, pady=(0, 8))
        row_idx += 1

        footer = ctk.CTkFrame(self.scroll, fg_color=HEADER_BG, corner_radius=12, height=120)
        footer.grid(row=row_idx, column=0, sticky="ew", padx=0, pady=(10, 8))
        footer.grid_propagate(False)

        ctk.CTkLabel(
            footer,
            text="Design made by: Arsen, Eldiar\nPRG-28B",
            font=ctk.CTkFont(family="Courier New", size=16, weight="bold"),
            text_color="white", justify="center",
        ).place(relx=0.5, rely=0.35, anchor="center")

        ctk.CTkLabel(
            footer,
            text="La Masia Team",
            font=ctk.CTkFont(family="Courier New", size=18, weight="bold"),
            text_color="white",
        ).place(relx=0.5, rely=0.72, anchor="center")

        ctk.CTkLabel(
            footer,
            text="⭐ UEFA\nCHAMPIONS\nLEAGUE",
            font=ctk.CTkFont(family="Arial", size=10, weight="bold"),
            text_color="white", justify="center",
        ).place(x=60, rely=0.5, anchor="center")