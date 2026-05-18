from __future__ import annotations

import base64
import hashlib
import logging
import math
import tkinter as tk
from datetime import datetime
from pathlib import Path
from typing import Callable
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

import customtkinter as ctk

from config import (
    APP_BG,
    CARD_BG,
    CARD_BORDER,
    CARD_SHADOW,
    COL_WIDTHS,
    COMPETITIONS,
    CompetitionConfig,
    FORM_DRAW,
    FORM_LOSS,
    FORM_WIN,
    LINK_COLOR,
    MUTED_TEXT,
    OUTER_BG,
    ROW_ALT_BG,
    ROW_BG,
    SCROLLBAR_COLOR,
    SCROLLBAR_HOVER,
    SECTIONS,
    SECTION_BG,
    SEPARATOR_COLOR,
    SUBTEXT_COLOR,
    TEXT_COLOR,
    ZONE_COLORS,
)
from i18n import SEASONS, get_competition_title, get_table_strings
from models import Team
from espn_logos import ESPNLogoManager
from final_stages import FinalStagesWindow
from transfermarkt_logos import TransfermarktLogoManager

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

logger = logging.getLogger(__name__)
IMAGE_CACHE_DIR = Path(__file__).parent / ".cache" / "images"
REMOTE_HEADERS = {
    "user-agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/136.0.0.0 Safari/537.36"
    )
}


class GradientFrame(ctk.CTkFrame):
    def __init__(self, master: ctk.CTkBaseClass, colors: tuple[str, str], height: int, **kwargs) -> None:
        super().__init__(master, fg_color=colors[0], corner_radius=0, height=height, **kwargs)
        self.colors = colors
        self.canvas = tk.Canvas(self, highlightthickness=0, bd=0, bg=colors[0])
        self.canvas.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.after_idle(lambda: self.canvas.tk.call("lower", self.canvas._w))
        self.bind("<Configure>", self._redraw)

    def set_colors(self, colors: tuple[str, str]) -> None:
        self.colors = colors
        self.configure(fg_color=colors[0])
        self.canvas.configure(bg=colors[0])
        self._redraw()

    def _redraw(self, _event: object | None = None) -> None:
        width = max(self.winfo_width(), 2)
        height = max(self.winfo_height(), 2)
        self.canvas.configure(width=width, height=height)
        self.canvas.delete("grad")

        r1, g1, b1 = self._hex_to_rgb(self.colors[0])
        r2, g2, b2 = self._hex_to_rgb(self.colors[1])
        for x in range(width):
            ratio = x / max(width - 1, 1)
            r = int(r1 + (r2 - r1) * ratio)
            g = int(g1 + (g2 - g1) * ratio)
            b = int(b1 + (b2 - b1) * ratio)
            color = f"#{r:02x}{g:02x}{b:02x}"
            self.canvas.create_line(x, 0, x, height, fill=color, tags="grad")

    @staticmethod
    def _hex_to_rgb(color: str) -> tuple[int, int, int]:
        color = color.lstrip("#")
        return int(color[0:2], 16), int(color[2:4], 16), int(color[4:6], 16)


class LeagueTableApp(ctk.CTk):
    def __init__(
        self,
        competition_key: str = "ucl",
        season_key: str = "2526",
        language: str = "English",
        on_home: Callable[[], None] | None = None,
    ) -> None:
        super().__init__()
        self.on_home_callback = on_home
        self.language = language
        self.season_key = season_key
        self.competition: CompetitionConfig = COMPETITIONS[competition_key]
        self.title(get_competition_title(self.language, self.competition.key, self.competition.app_title))
        self.geometry("1440x900")
        self.minsize(1240, 820)
        self.configure(fg_color=APP_BG)
        self.protocol("WM_DELETE_WINDOW", self._close_window)

        self.teams: list[Team] = []
        self.last_update: str = self._display_timestamp(None)
        self.is_fallback_data = False
        self.no_season_data = False
        self.nav_buttons: list[ctk.CTkButton] = []
        self.final_stages_window: FinalStagesWindow | None = None
        self.logo_images: dict[str, tk.PhotoImage] = {}
        self.espn_logos = ESPNLogoManager()
        self.espn_logo_placeholder = self.espn_logos.get_placeholder((24, 24))
        self.transfermarkt_logos = TransfermarktLogoManager()
        self.team_logo_placeholder = self.transfermarkt_logos.get_placeholder((24, 24))
        self.table_inner_width = sum(COL_WIDTHS) + 32

        self._build_shell()
        self.espn_logos.start_ui_pump(self)
        self.transfermarkt_logos.start_ui_pump(self)
        self._apply_competition_ui()
        self._render_table()
        self.after(100, self.refresh_from_api)

    @property
    def strings(self) -> dict[str, object]:
        return get_table_strings(self.language)

    def set_teams(self, teams: list[Team], last_update: str | None = None, is_fallback: bool = False) -> None:
        self.teams = teams
        self.is_fallback_data = is_fallback
        self.last_update = self._display_timestamp(last_update)
        self._update_header()
        self._render_table()

    def switch_competition(self, competition_key: str) -> None:
        if competition_key == self.competition.key:
            return

        self.competition = COMPETITIONS[competition_key]
        self.teams = []
        self.is_fallback_data = False
        self.no_season_data = False
        self.last_update = self._display_timestamp(None)
        self._apply_competition_ui()
        self._render_table()
        self.after(50, self.refresh_from_api)

    def switch_season(self, season_key: str) -> None:
        if season_key == self.season_key:
            return
        self.season_key = season_key
        self.teams = []
        self.is_fallback_data = False
        self.no_season_data = False
        self.last_update = self._display_timestamp(None)
        self._update_header()
        self._render_table()
        self.after(50, self.refresh_from_api)

    def refresh_from_api(self) -> None:
        try:
            from api import NoSeasonDataError, SofaScoreApiClient

            logging.basicConfig(level=logging.INFO)
            logger.info("Fetching %s standings (season=%s)", self.competition.short_title, self.season_key)

            client = SofaScoreApiClient()
            teams, last_update, is_fallback = client.get_standings(self.competition, season_key=self.season_key)
            if teams:
                self.set_teams(teams, last_update, is_fallback)
            else:
                self._load_mock_data()
        except NoSeasonDataError as exc:
            logger.info("%s", exc)
            self.no_season_data = True
            self.teams = []
            self.is_fallback_data = False
            self.last_update = self._display_timestamp(None)
            self._update_header()
            self._render_table()
        except Exception as exc:
            logger.error("Failed to fetch %s data: %s", self.competition.short_title, exc)
            self._load_mock_data()

    def _load_mock_data(self) -> None:
        try:
            from mock_data import get_mock_teams

            teams = get_mock_teams(self.competition.key)
            self.set_teams(teams, "20 Feb 2026", is_fallback=True)
        except Exception:
            self.last_update = "20 Feb 2026"
            self._update_header()

    def _build_shell(self) -> None:
        self.header = GradientFrame(self, self.competition.header_gradient, height=150)
        self.header.pack(fill="x", side="top")
        self.header.pack_propagate(False)

        self.header_left = ctk.CTkFrame(self.header, fg_color="transparent")
        self.header_left.place(x=48, y=44)

        self.title_label = ctk.CTkLabel(
            self.header_left,
            text="",
            font=ctk.CTkFont(family="Arial", size=32, weight="bold"),
            text_color="white",
        )
        self.title_label.pack(anchor="w")

        self.season_label = ctk.CTkLabel(
            self.header_left,
            text="",
            font=ctk.CTkFont(family="Arial", size=14),
            text_color="#CED7FF",
        )
        self.season_label.pack(anchor="w", pady=(3, 0))

        self.home_btn = ctk.CTkButton(
            self.header,
            text="",
            command=self._go_home,
            width=92,
            height=32,
            corner_radius=12,
            font=ctk.CTkFont(family="Arial", size=13, weight="bold"),
            fg_color="#FFFFFF",
            text_color="#101010",
            hover_color="#EDEDED",
        )
        self.home_btn.place(x=48, y=10)

        self.nav_frame = ctk.CTkFrame(self.header, fg_color="transparent")
        self.nav_frame.place(relx=0.5, y=12, anchor="n")

        self.final_stages_btn = ctk.CTkButton(
            self.header,
            text="",
            command=self._open_final_stages,
            width=136,
            height=36,
            corner_radius=12,
            font=ctk.CTkFont(family="Arial", size=13, weight="bold"),
            fg_color="#FFFFFF",
            text_color="#101010",
            hover_color="#EDEDED",
            border_width=1,
            border_color="#D6D6D6",
        )
        self.final_stages_btn.place(relx=0.5, y=66, anchor="n")

        self.season_toggle_frame = ctk.CTkFrame(self.header, fg_color="transparent")
        self.season_toggle_frame.place(relx=1.0, x=-36, y=8, anchor="ne")

        self.header_right = ctk.CTkFrame(self.header, fg_color="transparent")
        self.header_right.place(relx=1.0, x=-36, y=82, anchor="ne")

        self.matchday_label = ctk.CTkLabel(
            self.header_right,
            text="",
            font=ctk.CTkFont(family="Arial", size=13),
            text_color=MUTED_TEXT,
        )
        self.matchday_label.pack(anchor="e")

        self.timestamp_label = ctk.CTkLabel(
            self.header_right,
            text="",
            font=ctk.CTkFont(family="Arial", size=13),
            text_color=MUTED_TEXT,
        )
        self.timestamp_label.pack(anchor="e", pady=(2, 0))

        self.outer = ctk.CTkFrame(self, fg_color=OUTER_BG, corner_radius=0)
        self.outer.pack(fill="both", expand=True)

        self.scroll = ctk.CTkScrollableFrame(
            self.outer,
            fg_color=OUTER_BG,
            corner_radius=0,
            scrollbar_button_color=SCROLLBAR_COLOR,
            scrollbar_button_hover_color=SCROLLBAR_HOVER,
        )
        self.scroll.pack(fill="both", expand=True, padx=0, pady=0)
        self.scroll.grid_columnconfigure(0, weight=1)

    def _go_home(self) -> None:
        self._close_window()
        if self.on_home_callback:
            self.on_home_callback()

    def _open_final_stages(self) -> None:
        if self.final_stages_window is not None and self.final_stages_window.winfo_exists():
            self.final_stages_window.lift()
            self.final_stages_window.focus_force()
            return
        self.final_stages_window = FinalStagesWindow(self, self.competition.key, self.language)

    def _close_window(self) -> None:
        try:
            self.tk.eval(
                """
                proc bgerror {msg} {
                    if {[string match "*invalid command name*" $msg]} {return}
                }
                """
            )
        except tk.TclError:
            pass
        self.destroy()

    def _apply_competition_ui(self) -> None:
        self.header.set_colors(self.competition.header_gradient)
        self._update_header()
        self._rebuild_nav()
        self._rebuild_season_toggle()

    def _update_header(self) -> None:
        strings = self.strings
        title = get_competition_title(self.language, self.competition.key, self.competition.title)
        self.title_label.configure(text=title)
        self.home_btn.configure(text=str(strings["go_home"]))
        self.final_stages_btn.configure(text=str(strings["final_stages"]))

        phase_labels = strings.get("phase_labels", {})
        season_label = next((item["label"] for item in SEASONS if item["key"] == self.season_key), "2025 / 26")
        phase_template = phase_labels.get(self.season_key, "League Phase {season}") if isinstance(phase_labels, dict) else "League Phase {season}"
        if self.is_fallback_data:
            mock_template = str(strings.get("mock_data", "League Phase {season} (Mock Data - API Unavailable)"))
            subtitle = mock_template.format(season=season_label.replace(" ", ""))
        else:
            subtitle = str(phase_template).format(season=season_label.replace(" ", ""))
        self.season_label.configure(text=subtitle)

        matchday_template = str(strings["matchday"])
        self.matchday_label.configure(
            text=matchday_template.format(
                current=self.competition.matchday_current,
                total=self.competition.matchday_total,
            )
        )
        self.timestamp_label.configure(text=f"{strings['last_updated']}: {self.last_update}")
        self.title(f"{title} · {season_label}")

    def _rebuild_nav(self) -> None:
        for widget in self.nav_frame.winfo_children():
            widget.destroy()

        self.nav_buttons = []
        nav_template = str(self.strings["nav_to"])
        for index, target in enumerate(self.competition.nav_targets):
            cfg = COMPETITIONS[target]
            button = ctk.CTkButton(
                self.nav_frame,
                text=nav_template.format(name=get_competition_title(self.language, target, cfg.short_title)),
                command=lambda key=target: self.switch_competition(key),
                width=126,
                height=42,
                corner_radius=12,
                font=ctk.CTkFont(family="Arial", size=13, weight="bold"),
                fg_color="#FFFFFF",
                text_color="#101010",
                hover_color="#EDEDED",
                border_width=1,
                border_color="#D6D6D6",
            )
            button.grid(row=0, column=index, padx=18)
            self.nav_buttons.append(button)

    def _rebuild_season_toggle(self) -> None:
        for widget in self.season_toggle_frame.winfo_children():
            widget.destroy()

        self.season_menu = ctk.CTkOptionMenu(
            self.season_toggle_frame,
            values=[item["label"] for item in SEASONS],
            command=self._on_season_select,
            width=120,
            height=28,
            corner_radius=8,
            font=ctk.CTkFont(family="Arial", size=11, weight="bold"),
            fg_color="#5A6A99",
            button_color="#4A5A89",
            button_hover_color="#3A4A79",
            text_color="#FFFFFF",
        )
        self.season_menu.grid(row=0, column=0, padx=3)
        current_label = next((item["label"] for item in SEASONS if item["key"] == self.season_key), "2025 / 26")
        self.season_menu.set(current_label)

    def _on_season_select(self, value: str) -> None:
        key = next((item["key"] for item in SEASONS if item["label"] == value), "2526")
        self.switch_season(key)

    def _render_table(self) -> None:
        for widget in self.scroll.winfo_children():
            widget.destroy()

        card_shadow = ctk.CTkFrame(self.scroll, fg_color=CARD_SHADOW, corner_radius=18, height=10)
        card_shadow.grid(row=0, column=0, sticky="ew", padx=82, pady=(26, 0))

        card = ctk.CTkFrame(
            self.scroll,
            fg_color=CARD_BG,
            corner_radius=18,
            border_width=1,
            border_color=CARD_BORDER,
        )
        card.grid(row=0, column=0, sticky="ew", padx=74, pady=(18, 0))
        card.grid_columnconfigure(0, weight=1)

        table = ctk.CTkFrame(card, fg_color="transparent")
        table.grid(row=0, column=0, sticky="w", pady=(0, 0), padx=(0, 0))
        table.grid_columnconfigure(0, weight=0)

        if self.no_season_data:
            self._render_no_season_data(card)
            self._render_footer(2)
            return

        sorted_teams = sorted(self.teams, key=lambda team: team.sort_key())
        self._render_header_row(table)

        row_idx = 1
        for sec_start, sec_end, sec_key in SECTIONS:
            row_idx = self._render_section_header(table, row_idx, sec_key)
            for pos_in_section, team in enumerate(sorted_teams[sec_start:sec_end]):
                global_pos = sec_start + pos_in_section + 1
                row_idx = self._render_team_row(table, row_idx, global_pos, team, sec_key, pos_in_section % 2 == 1)

        self._render_disclaimer(row_idx + 1)
        self._render_footer(row_idx + 2)

    def _render_no_season_data(self, parent: ctk.CTkFrame) -> None:
        strings = self.strings
        empty = ctk.CTkFrame(parent, fg_color="transparent", height=280)
        empty.grid(row=0, column=0, sticky="ew", padx=28, pady=34)
        empty.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            empty,
            text=str(strings["no_season_data_title"]),
            font=ctk.CTkFont(family="Arial", size=28, weight="bold"),
            text_color=TEXT_COLOR,
        ).grid(row=0, column=0, pady=(48, 12))

        ctk.CTkLabel(
            empty,
            text=str(strings["no_season_data_message"]),
            font=ctk.CTkFont(family="Arial", size=16),
            text_color=SUBTEXT_COLOR,
            wraplength=680,
            justify="center",
        ).grid(row=1, column=0, pady=(0, 28))

        ctk.CTkButton(
            empty,
            text=str(strings["go_home"]),
            command=self._go_home,
            width=150,
            height=42,
            corner_radius=14,
            font=ctk.CTkFont(family="Arial", size=14, weight="bold"),
            fg_color=self.competition.header_gradient[0],
            hover_color=self.competition.header_gradient[1],
            text_color="white",
        ).grid(row=2, column=0)

    def _render_header_row(self, parent: ctk.CTkFrame) -> None:
        headers = self.strings["columns"]
        hdr = ctk.CTkFrame(parent, fg_color="#0C1874", height=42, corner_radius=8)
        hdr.grid(row=0, column=0, sticky="ew", padx=12, pady=(14, 6))
        for column, width in enumerate(COL_WIDTHS):
            hdr.grid_columnconfigure(column, weight=0, minsize=width)

        for column, (text, width) in enumerate(zip(headers, COL_WIDTHS)):
            anchor = "w" if column == 1 else "center"
            ctk.CTkLabel(
                hdr,
                text=str(text),
                width=width,
                font=ctk.CTkFont(family="Arial", size=11, weight="bold"),
                text_color="#EAF0FF",
                anchor=anchor,
            ).grid(
                row=0,
                column=column,
                padx=(10, 6) if column == 1 else (4, 4),
                pady=10,
                sticky="w" if column == 1 else "",
            )

    def _render_section_header(self, parent: ctk.CTkFrame, row_idx: int, section_key: str) -> int:
        sections = self.strings["sections"]
        label = sections.get(section_key, section_key) if isinstance(sections, dict) else section_key
        section = ctk.CTkFrame(parent, fg_color=SECTION_BG, corner_radius=0, height=30)
        section.grid(row=row_idx, column=0, sticky="ew", padx=12, pady=(0, 0))
        section.grid_columnconfigure(0, weight=1)
        ctk.CTkFrame(section, fg_color=SEPARATOR_COLOR, height=1).place(relx=0.0, rely=0.0, relwidth=1.0)
        ctk.CTkLabel(
            section,
            text=str(label),
            font=ctk.CTkFont(family="Arial", size=11),
            text_color=TEXT_COLOR,
            anchor="w",
        ).pack(side="left", padx=(12, 0), pady=7)
        ctk.CTkFrame(section, fg_color=SEPARATOR_COLOR, height=1).place(relx=0.0, rely=1.0, relwidth=1.0, anchor="sw")
        return row_idx + 1

    def _render_team_row(
        self,
        parent: ctk.CTkFrame,
        row_idx: int,
        pos: int,
        team: Team,
        zone_key: str,
        is_alt: bool,
    ) -> int:
        row = ctk.CTkFrame(parent, fg_color=ROW_ALT_BG if is_alt else ROW_BG, height=44, corner_radius=0)
        row.grid(row=row_idx, column=0, sticky="ew", padx=12, pady=0)
        row.grid_propagate(False)
        for column, width in enumerate(COL_WIDTHS):
            row.grid_columnconfigure(column, weight=0, minsize=width)

        ctk.CTkFrame(row, fg_color=ZONE_COLORS[zone_key], width=2, corner_radius=0).place(x=0, y=0, relheight=1.0)

        ctk.CTkLabel(
            row,
            text=str(pos),
            width=COL_WIDTHS[0],
            font=ctk.CTkFont(family="Arial", size=12),
            text_color=TEXT_COLOR,
        ).grid(row=0, column=0, padx=(8, 4), pady=7)

        self._render_club_cell(row, team, 1)

        stats = [team.pld, team.w, team.d, team.l, team.gf, team.ga, team.gd, team.pts]
        for stat, column in zip(stats, range(2, 10)):
            ctk.CTkLabel(
                row,
                text=str(stat),
                width=COL_WIDTHS[column],
                font=ctk.CTkFont(family="Arial", size=12, weight="bold" if column == 9 else "normal"),
                text_color=TEXT_COLOR,
            ).grid(row=0, column=column, padx=(4, 4), pady=7)

        self._render_form(row, team, 10)
        return row_idx + 1

    def _render_club_cell(self, parent: ctk.CTkFrame, team: Team, column: int) -> None:
        club = ctk.CTkFrame(parent, fg_color="transparent", width=COL_WIDTHS[column], height=32)
        club.grid(row=0, column=column, padx=(8, 0), pady=5, sticky="w")
        club.grid_propagate(False)
        club.grid_columnconfigure(3, weight=1)

        self._render_flag(club, team, 0)
        self._render_badge(club, team, 1)

        ctk.CTkLabel(
            club,
            text=team.name,
            font=ctk.CTkFont(family="Arial", size=12),
            text_color=TEXT_COLOR,
            anchor="w",
        ).grid(row=0, column=3, padx=(12, 0), sticky="w")

    def _render_flag(self, parent: ctk.CTkFrame, team: Team, column: int) -> None:
        frame = ctk.CTkFrame(parent, fg_color="transparent", width=30, height=22)
        frame.grid(row=0, column=column, padx=(0, 8))
        frame.grid_propagate(False)

        image = self._get_remote_image(team.country_flag_url, f"flag:{team.country_alpha2 or team.country_name}", 26, 18)
        if image is not None:
            label = tk.Label(frame, image=image, bd=0, highlightthickness=0, bg=ROW_BG)
            label.image = image
            label.place(relx=0.5, rely=0.5, anchor="center")
            return

        fallback = team.flag_emoji or (team.country_alpha2 or "•")[:2]
        ctk.CTkLabel(
            frame,
            text=fallback,
            font=ctk.CTkFont(family="Segoe UI Emoji", size=15, weight="bold"),
            text_color=TEXT_COLOR,
        ).place(relx=0.5, rely=0.5, anchor="center")

    def _render_badge(self, parent: ctk.CTkFrame, team: Team, column: int) -> None:
        frame = ctk.CTkFrame(parent, fg_color="transparent", width=28, height=28)
        frame.grid(row=0, column=column, padx=(0, 0))
        frame.grid_propagate(False)

        image = self._get_remote_image(team.team_logo_url, f"logo:{team.team_id or team.name}", 24, 24)
        if image is not None:
            label = tk.Label(frame, image=image, bd=0, highlightthickness=0, bg=ROW_BG)
            label.image = image
            label.place(relx=0.5, rely=0.5, anchor="center")
            return

        if team.espn_id is not None:
            label = ctk.CTkLabel(frame, text="", image=self.espn_logo_placeholder)
            label.image = self.espn_logo_placeholder
            label.place(relx=0.5, rely=0.5, anchor="center")
            self.espn_logos.load_logo_async(
                team.espn_id,
                (24, 24),
                lambda image, target=label: self._set_ctk_image(target, image),
            )
            return

        if team.transfermarkt_id is not None and self.transfermarkt_logos.has_cached_logo(team.transfermarkt_id):
            label = ctk.CTkLabel(frame, text="", image=self.team_logo_placeholder)
            label.image = self.team_logo_placeholder
            label.place(relx=0.5, rely=0.5, anchor="center")
            self.transfermarkt_logos.load_logo_async(
                team.transfermarkt_id,
                (24, 24),
                lambda image, target=label: self._set_ctk_image(target, image),
            )
            return

        canvas = tk.Canvas(frame, width=28, height=28, highlightthickness=0, bd=0, bg=ROW_BG)
        canvas.place(relx=0.5, rely=0.5, anchor="center")
        self._draw_gradient_rect(canvas, 0, 0, 28, 28, self.competition.badge_gradient, radius=8)
        canvas.create_text(14, 14, text=team.abbr[:2].upper(), fill="white", font=("Arial", 8, "bold"))

    def _render_form(self, parent: ctk.CTkFrame, team: Team, column: int) -> None:
        frame = ctk.CTkFrame(parent, fg_color="transparent", width=COL_WIDTHS[column], height=26)
        frame.grid(row=0, column=column, padx=(6, 8), pady=5)
        frame.grid_propagate(False)

        results = team.form[:5]
        if not results:
            ctk.CTkLabel(frame, text="-", font=ctk.CTkFont(size=12), text_color=SUBTEXT_COLOR).place(relx=0.5, rely=0.5, anchor="center")
            return

        content = ctk.CTkFrame(frame, fg_color="transparent")
        content.place(relx=1.0, rely=0.5, anchor="e", x=-8)
        for index, result in enumerate(results):
            color = FORM_WIN if result == "W" else FORM_LOSS if result == "L" else FORM_DRAW
            canvas = tk.Canvas(content, width=18, height=18, highlightthickness=0, bd=0, bg=ROW_BG)
            canvas.grid(row=0, column=index, padx=1)
            canvas.create_oval(1, 1, 17, 17, fill=color, outline=color)
            canvas.create_text(9, 9, text=result, fill="#101010" if result != "L" else "white", font=("Arial", 7, "bold"))

    def _render_disclaimer(self, row_idx: int) -> None:
        strings = self.strings
        wrap = ctk.CTkFrame(self.scroll, fg_color="transparent")
        wrap.grid(row=row_idx, column=0, sticky="ew", padx=74, pady=(14, 8))

        dot = tk.Canvas(wrap, width=16, height=16, highlightthickness=0, bd=0, bg=APP_BG)
        dot.grid(row=0, column=0, sticky="nw", padx=(0, 16), pady=(0, 0))
        dot.create_oval(4, 4, 12, 12, fill=self.competition.header_gradient[0], outline=self.competition.header_gradient[0])

        text_wrap = ctk.CTkFrame(wrap, fg_color="transparent")
        text_wrap.grid(row=0, column=1, sticky="w")

        ctk.CTkLabel(
            text_wrap,
            text=str(strings["qualified"]),
            font=ctk.CTkFont(family="Arial", size=12),
            text_color=TEXT_COLOR,
            anchor="w",
        ).pack(anchor="w")

        ctk.CTkLabel(
            text_wrap,
            text=str(strings["regulations"]),
            font=ctk.CTkFont(family="Arial", size=12),
            text_color=LINK_COLOR,
            anchor="w",
        ).pack(anchor="w")

        ctk.CTkLabel(
            text_wrap,
            text=str(strings["disclaimer"]),
            font=ctk.CTkFont(family="Arial", size=11),
            text_color=TEXT_COLOR,
            justify="left",
            anchor="w",
            wraplength=1110,
        ).pack(anchor="w", pady=(10, 0))

    def _render_footer(self, row_idx: int) -> None:
        footer = GradientFrame(self.scroll, self.competition.footer_gradient, height=150)
        footer.grid(row=row_idx, column=0, sticky="ew", padx=0, pady=(12, 0))
        footer.grid_propagate(False)

        logo_canvas = tk.Canvas(footer, width=180, height=110, highlightthickness=0, bd=0, bg=footer.colors[0])
        logo_canvas.place(x=34, rely=0.5, anchor="w")
        self._render_logo(logo_canvas)

        ctk.CTkLabel(
            footer,
            text=str(self.strings["footer_design"]),
            font=ctk.CTkFont(family="Arial", size=18, weight="bold"),
            text_color="white",
            justify="center",
        ).place(relx=0.54, rely=0.40, anchor="center")

        ctk.CTkLabel(
            footer,
            text=str(self.strings["footer_team"]),
            font=ctk.CTkFont(family="Arial", size=18, weight="bold"),
            text_color="white",
        ).place(relx=0.54, rely=0.72, anchor="center")

    def _render_logo(self, canvas: tk.Canvas) -> None:
        image = self._get_logo_image(self.competition.logo_path, max_width=135, max_height=105)
        if image is not None:
            canvas.delete("all")
            canvas.create_image(90, 55, image=image)
            return
        self._draw_logo_fallback(canvas)

    def _get_logo_image(self, path: str, max_width: int, max_height: int) -> tk.PhotoImage | None:
        cache_key = f"{self.competition.key}:{path}:{max_width}x{max_height}"
        if cache_key in self.logo_images:
            return self.logo_images[cache_key]
        if not Path(path).exists():
            return None
        try:
            image = tk.PhotoImage(file=path)
            scale = max(1, math.ceil(image.width() / max_width), math.ceil(image.height() / max_height))
            if scale > 1:
                image = image.subsample(scale, scale)
            self.logo_images[cache_key] = image
            return image
        except tk.TclError:
            return None

    def _get_remote_image(self, url: str | None, cache_key: str, max_width: int, max_height: int) -> tk.PhotoImage | None:
        if not url:
            return None
        key = f"{cache_key}:{max_width}x{max_height}"
        if key in self.logo_images:
            return self.logo_images[key]

        IMAGE_CACHE_DIR.mkdir(parents=True, exist_ok=True)
        suffix = Path(url).suffix or ".png"
        disk_key = hashlib.sha256(url.encode("utf-8")).hexdigest()
        cache_path = IMAGE_CACHE_DIR / f"{disk_key}{suffix}"

        raw: bytes | None = None
        try:
            if cache_path.exists():
                raw = cache_path.read_bytes()
            else:
                request = Request(url, headers=REMOTE_HEADERS)
                with urlopen(request, timeout=4) as response:
                    raw = response.read()
                if raw:
                    cache_path.write_bytes(raw)
        except (HTTPError, URLError, TimeoutError, OSError) as exc:
            logger.debug("Image fetch failed for %s: %s", url, exc)
            return None

        if not raw:
            return None

        try:
            image = tk.PhotoImage(data=base64.b64encode(raw).decode("ascii"))
            scale = max(1, math.ceil(image.width() / max_width), math.ceil(image.height() / max_height))
            if scale > 1:
                image = image.subsample(scale, scale)
            self.logo_images[key] = image
            return image
        except tk.TclError:
            return None

    def _draw_logo_fallback(self, canvas: tk.Canvas) -> None:
        canvas.delete("all")
        if self.competition.key == "ucl":
            canvas.create_oval(60, 6, 150, 96, outline="white", width=3)
            for points in (
                (104, 6, 115, 22, 132, 24, 120, 36, 124, 54, 106, 44, 88, 52, 92, 34, 78, 24, 96, 22),
                (68, 26, 84, 20, 92, 38, 84, 54, 66, 46),
                (128, 28, 142, 40, 134, 58, 118, 52, 116, 36),
                (82, 58, 96, 52, 108, 66, 98, 84, 80, 76),
                (112, 68, 126, 58, 140, 74, 128, 90, 110, 84),
            ):
                canvas.create_polygon(*points, fill="white", outline="white")
            canvas.create_arc(72, 96, 140, 132, start=25, extent=130, style="arc", outline="white", width=4)
        elif self.competition.key == "uel":
            canvas.create_oval(66, 14, 146, 94, outline="white", width=3)
            canvas.create_polygon(92, 16, 102, 18, 98, 116, 88, 114, fill="white", outline="white")
            canvas.create_polygon(110, 16, 122, 18, 116, 114, 106, 112, fill="white", outline="white")
            canvas.create_polygon(101, 18, 109, 18, 114, 104, 106, 122, 96, 102, fill="#000000", outline="#000000")
            canvas.create_arc(76, 104, 134, 136, start=20, extent=140, style="arc", outline="white", width=4)
        else:
            green = self.competition.header_gradient[0]
            canvas.create_arc(62, 20, 96, 108, start=80, extent=180, style="arc", outline=green, width=8)
            canvas.create_arc(116, 20, 150, 108, start=-80, extent=180, style="arc", outline=green, width=8)
            canvas.create_polygon(92, 18, 100, 16, 102, 86, 92, 116, 84, 84, fill="white", outline="white")
            canvas.create_polygon(102, 16, 112, 16, 112, 84, 104, 112, 98, 86, fill="white", outline="white")
            canvas.create_polygon(112, 16, 120, 18, 120, 80, 112, 108, 108, 84, fill="white", outline="white")
            canvas.create_polygon(86, 116, 118, 116, 122, 132, 82, 132, fill="white", outline="white")
            canvas.create_arc(76, 104, 134, 136, start=20, extent=140, style="arc", outline="white", width=4)
        canvas.create_text(
            105,
            150,
            text="\n".join(self.competition.logo_lines),
            fill="white",
            font=("Arial", 17, "bold"),
            justify="center",
        )

    @staticmethod
    def _draw_gradient_rect(
        canvas: tk.Canvas,
        x1: int,
        y1: int,
        x2: int,
        y2: int,
        colors: tuple[str, str],
        radius: int = 0,
    ) -> None:
        r1, g1, b1 = GradientFrame._hex_to_rgb(colors[0])
        r2, g2, b2 = GradientFrame._hex_to_rgb(colors[1])
        width = max(x2 - x1, 1)
        height = max(y2 - y1, 1)
        radius = max(0, min(radius, width // 2, height // 2))

        for x in range(width):
            ratio = x / max(width - 1, 1)
            r = int(r1 + (r2 - r1) * ratio)
            g = int(g1 + (g2 - g1) * ratio)
            b = int(b1 + (b2 - b1) * ratio)
            y_offset = 0.0
            if radius > 0:
                if x < radius:
                    dx = radius - x - 0.5
                    y_offset = radius - math.sqrt(max(radius * radius - dx * dx, 0))
                elif x >= width - radius:
                    dx = x - (width - radius) + 0.5
                    y_offset = radius - math.sqrt(max(radius * radius - dx * dx, 0))

            top = y1 + int(y_offset)
            bottom = y2 - int(y_offset)
            canvas.create_line(x1 + x, top, x1 + x, bottom, fill=f"#{r:02x}{g:02x}{b:02x}")

    @staticmethod
    def _display_timestamp(value: str | None) -> str:
        if value:
            for fmt in ("%d %b %Y, %H:%M", "%d %b %Y"):
                try:
                    return datetime.strptime(value, fmt).strftime("%d %b %Y")
                except ValueError:
                    continue
            return value
        return datetime.now().strftime("%d %b %Y")

    @staticmethod
    def _set_ctk_image(label: ctk.CTkLabel, image: ctk.CTkImage) -> None:
        if not label.winfo_exists():
            return
        label.configure(image=image)
        label.image = image
