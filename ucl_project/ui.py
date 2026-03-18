from __future__ import annotations

import logging
import math
import tkinter as tk
from datetime import datetime
from pathlib import Path

import customtkinter as ctk

from config import (
    APP_BG,
    CARD_BG,
    CARD_BORDER,
    CARD_SHADOW,
    COL_HEADERS,
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
    SECTION_BG,
    SECTIONS,
    SEPARATOR_COLOR,
    SUBTEXT_COLOR,
    TEXT_COLOR,
    ZONE_COLORS,
)
from models import Team

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")


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
    def __init__(self) -> None:
        super().__init__()
        self.competition: CompetitionConfig = COMPETITIONS["ucl"]
        self.title(self.competition.app_title)
        self.geometry("1440x900")
        self.minsize(1240, 820)
        self.configure(fg_color=APP_BG)

        self.teams: list[Team] = []
        self.last_update: str = self._display_timestamp(None)
        self.is_fallback_data: bool = False
        self.nav_buttons: list[ctk.CTkButton] = []
        self.logo_images: dict[str, tk.PhotoImage] = {}
        self.table_inner_width = sum(COL_WIDTHS) + 88

        self._build_shell()
        self._apply_competition_ui()
        self._render_table()
        self.after(100, self.refresh_from_api)

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
        self.last_update = self._display_timestamp(None)
        self._apply_competition_ui()
        self._render_table()
        self.after(50, self.refresh_from_api)

    def refresh_from_api(self) -> None:
        try:
            from api import SofaScoreApiClient

            logging.basicConfig(level=logging.INFO)
            logger = logging.getLogger(__name__)
            logger.info("Fetching %s standings", self.competition.short_title)

            client = SofaScoreApiClient()
            teams, last_update, is_fallback = client.get_standings(self.competition)
            if teams:
                self.set_teams(teams, last_update, is_fallback)
            else:
                self._load_mock_data()
        except Exception as exc:
            logging.getLogger(__name__).error("Failed to fetch %s data: %s", self.competition.short_title, exc)
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
        self.header = GradientFrame(self, self.competition.header_gradient, height=148)
        self.header.pack(fill="x", side="top")
        self.header.pack_propagate(False)

        self.header_content = self.header
        self.header_left = ctk.CTkFrame(self.header_content, fg_color="transparent")
        self.header_left.place(x=50, y=52)

        self.title_label = ctk.CTkLabel(
            self.header_left,
            text="",
            font=ctk.CTkFont(family="Arial", size=23, weight="bold"),
            text_color="white",
        )
        self.title_label.pack(anchor="w")

        self.season_label = ctk.CTkLabel(
            self.header_left,
            text="",
            font=ctk.CTkFont(family="Arial", size=13),
            text_color="#F2E7E7",
        )
        self.season_label.pack(anchor="w", pady=(2, 0))

        self.nav_frame = ctk.CTkFrame(self.header_content, fg_color="transparent")
        self.nav_frame.place(relx=0.5, y=4, anchor="n")

        self.header_right = ctk.CTkFrame(self.header_content, fg_color="transparent")
        self.header_right.place(relx=1.0, x=-36, y=54, anchor="ne")

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

    def _apply_competition_ui(self) -> None:
        self.title(self.competition.app_title)
        self.header.set_colors(self.competition.header_gradient)
        self._update_header()
        self._rebuild_nav()

    def _update_header(self) -> None:
        self.title_label.configure(text=self.competition.title)
        if self.is_fallback_data:
            self.season_label.configure(text=self.competition.mock_season_label)
        else:
            self.season_label.configure(text=self.competition.season_label)
        self.matchday_label.configure(text=self.competition.matchday_text)
        self.timestamp_label.configure(text=f"Last updated: {self.last_update}")

    def _rebuild_nav(self) -> None:
        for widget in self.nav_frame.winfo_children():
            widget.destroy()

        self.nav_buttons = []
        for index, target in enumerate(self.competition.nav_targets):
            cfg = COMPETITIONS[target]
            button = ctk.CTkButton(
                self.nav_frame,
                text=f"Go to {cfg.short_title}",
                command=lambda key=target: self.switch_competition(key),
                width=136,
                height=50,
                corner_radius=12,
                font=ctk.CTkFont(family="Arial", size=13, weight="bold"),
                fg_color="#FFFFFF",
                text_color="#101010",
                hover_color="#EDEDED",
                border_width=1,
                border_color="#D6D6D6",
            )
            button.grid(row=0, column=index, padx=28)
            self.nav_buttons.append(button)

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

        sorted_teams = sorted(self.teams, key=lambda team: team.sort_key())
        self._render_header_row(table)

        row_idx = 1
        for sec_start, sec_end, sec_label, sec_key in SECTIONS:
            row_idx = self._render_section_header(table, row_idx, sec_label, sec_key)
            for pos_in_section, team in enumerate(sorted_teams[sec_start:sec_end]):
                global_pos = sec_start + pos_in_section + 1
                row_idx = self._render_team_row(table, row_idx, global_pos, team, sec_key, pos_in_section % 2 == 1)

        self._render_disclaimer(row_idx + 1)
        self._render_footer(row_idx + 2)

    def _render_header_row(self, parent: ctk.CTkFrame) -> None:
        hdr = ctk.CTkFrame(parent, fg_color="transparent", height=44)
        hdr.grid(row=0, column=0, sticky="ew", padx=10, pady=(12, 0))
        for column in range(len(COL_HEADERS)):
            hdr.grid_columnconfigure(column, weight=0, minsize=COL_WIDTHS[column])

        for column, (text, width) in enumerate(zip(COL_HEADERS, COL_WIDTHS)):
            anchor = "w" if column == 2 else "center"
            ctk.CTkLabel(
                hdr,
                text=text,
                width=width,
                font=ctk.CTkFont(family="Arial", size=12, weight="bold"),
                text_color=TEXT_COLOR,
                anchor=anchor,
            ).grid(
                row=0,
                column=column,
                padx=(4, 8) if column >= 3 else (4, 4),
                pady=8,
                sticky="w" if column == 2 else "",
            )

    def _render_section_header(self, parent: ctk.CTkFrame, row_idx: int, label: str, zone_key: str) -> int:
        section = ctk.CTkFrame(parent, fg_color=SECTION_BG, corner_radius=0, height=38)
        section.grid(row=row_idx, column=0, sticky="ew", padx=0, pady=(2, 0))
        section.grid_columnconfigure(0, weight=1)
        ctk.CTkFrame(section, fg_color=ZONE_COLORS[zone_key], width=2, corner_radius=0).place(x=0, y=0, relheight=1.0)
        ctk.CTkLabel(
            section,
            text=label,
            font=ctk.CTkFont(family="Arial", size=12, weight="normal"),
            text_color=TEXT_COLOR,
            anchor="w",
        ).pack(side="left", padx=(14, 0), pady=8)
        ctk.CTkFrame(section, fg_color=SEPARATOR_COLOR, height=1).place(x=0, rely=1.0, relwidth=1.0, anchor="sw")
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
        row = ctk.CTkFrame(parent, fg_color=ROW_ALT_BG if is_alt else ROW_BG, height=50, corner_radius=0)
        row.grid(row=row_idx, column=0, sticky="ew", padx=0, pady=0)
        row.grid_propagate(False)
        for column in range(len(COL_HEADERS)):
            row.grid_columnconfigure(column, weight=0, minsize=COL_WIDTHS[column])

        ctk.CTkFrame(row, fg_color=ZONE_COLORS[zone_key], width=2, corner_radius=0).place(x=0, y=0, relheight=1.0)

        ctk.CTkLabel(
            row,
            text=str(pos),
            width=COL_WIDTHS[0],
            font=ctk.CTkFont(family="Arial", size=12),
            text_color=TEXT_COLOR,
        ).grid(row=0, column=0, padx=(10, 4), pady=10)

        self._render_badge(row, team, 1)

        ctk.CTkLabel(
            row,
            text=team.name,
            font=ctk.CTkFont(family="Arial", size=12),
            text_color=TEXT_COLOR,
            anchor="w",
        ).grid(row=0, column=2, padx=(18, 8), pady=10, sticky="w")

        stats = [team.pld, team.w, team.d, team.l, team.gf, team.ga, team.gd, team.pts]
        for stat, column in zip(stats, range(3, 11)):
            stat_wrap = ctk.CTkFrame(row, fg_color="transparent", width=COL_WIDTHS[column], height=24)
            stat_wrap.grid(row=0, column=column, padx=(4, 8), pady=10)
            stat_wrap.grid_propagate(False)

            ctk.CTkLabel(
                stat_wrap,
                text=str(stat),
                width=COL_WIDTHS[column],
                font=ctk.CTkFont(family="Arial", size=12, weight="bold" if column == 10 else "normal"),
                text_color=TEXT_COLOR,
                anchor="center",
            ).place(relx=0.5, rely=0.5, x=20, anchor="center")

        self._render_form(row, team, 11)
        return row_idx + 1

    def _render_badge(self, parent: ctk.CTkFrame, team: Team, column: int) -> None:
        canvas = tk.Canvas(parent, width=38, height=34, highlightthickness=0, bd=0, bg=ROW_BG)
        canvas.grid(row=0, column=column, padx=(4, 6), pady=8)
        self._draw_gradient_rect(canvas, 0, 0, 38, 34, self.competition.badge_gradient, radius=6)
        canvas.create_text(
            19,
            17,
            text=team.abbr[:2].upper(),
            fill="white",
            font=("Arial", 11, "bold"),
        )

    def _render_form(self, parent: ctk.CTkFrame, team: Team, column: int) -> None:
        frame = ctk.CTkFrame(parent, fg_color="transparent", width=COL_WIDTHS[column], height=24)
        frame.grid(row=0, column=column, padx=(4, 8), pady=6)
        frame.grid_propagate(False)

        content = ctk.CTkFrame(frame, fg_color="transparent", height=24)
        content.place(relx=0.5, rely=0.5, x=20, anchor="center")

        results = team.form[:5]
        for index, result in enumerate(results):
            color = FORM_WIN if result == "W" else (FORM_LOSS if result == "L" else FORM_DRAW)
            canvas = tk.Canvas(content, width=20, height=20, highlightthickness=0, bd=0, bg=ROW_BG)
            canvas.grid(row=0, column=index, padx=2)
            canvas.create_oval(1, 1, 19, 19, fill=color, outline=color)
            canvas.create_text(10, 10, text=result, fill="#101010" if result != "L" else "white", font=("Arial", 8, "bold"))

        if results:
            underline = ctk.CTkFrame(content, fg_color=FORM_WIN if results[-1] == "W" else FORM_LOSS, height=1, width=28)
            underline.grid(row=1, column=max(len(results) - 1, 0), sticky="e", padx=(0, 0), pady=(0, 0))
        else:
            ctk.CTkLabel(content, text="-", text_color=SUBTEXT_COLOR).grid(row=0, column=0)

    def _render_disclaimer(self, row_idx: int) -> None:
        wrap = ctk.CTkFrame(self.scroll, fg_color="transparent")
        wrap.grid(row=row_idx, column=0, sticky="ew", padx=74, pady=(12, 6))

        dot_color = self.competition.header_gradient[0]
        dot = tk.Canvas(wrap, width=16, height=16, highlightthickness=0, bd=0, bg=APP_BG)
        dot.grid(row=0, column=0, sticky="nw", padx=(0, 16), pady=(0, 0))
        dot.create_oval(4, 4, 12, 12, fill=dot_color, outline=dot_color)

        text_wrap = ctk.CTkFrame(wrap, fg_color="transparent")
        text_wrap.grid(row=0, column=1, sticky="w")

        ctk.CTkLabel(
            text_wrap,
            text="Qualified",
            font=ctk.CTkFont(family="Arial", size=12),
            text_color=TEXT_COLOR,
            anchor="w",
        ).pack(anchor="w")

        regulations = ctk.CTkLabel(
            text_wrap,
            text="Want to learn more about the format? Check the competition regulations",
            font=ctk.CTkFont(family="Arial", size=12),
            text_color=LINK_COLOR,
            anchor="w",
        )
        regulations.pack(anchor="w")

        ctk.CTkLabel(
            text_wrap,
            text=(
                "Standings are provisional until all league phase matches have been played and officially validated by UEFA. "
                "Confirmations of qualification / elimination are based on the provisional standings and are therefore for "
                "guidance purposes only until all league phase matches are completed and final standings have been validated by UEFA."
            ),
            font=ctk.CTkFont(family="Arial", size=11),
            text_color=TEXT_COLOR,
            justify="left",
            anchor="w",
            wraplength=1110,
        ).pack(anchor="w", pady=(12, 0))

    def _render_footer(self, row_idx: int) -> None:
        footer = GradientFrame(self.scroll, self.competition.footer_gradient, height=170)
        footer.grid(row=row_idx, column=0, sticky="ew", padx=0, pady=(12, 0))
        footer.grid_propagate(False)

        logo_canvas = tk.Canvas(footer, width=180, height=120, highlightthickness=0, bd=0, bg=footer.colors[0])
        logo_canvas.place(x=34, rely=0.5, anchor="w", y=0)
        self._render_logo(logo_canvas)

        ctk.CTkLabel(
            footer,
            text="Design made by: Arsen, Eldiar\nPRG-28B",
            font=ctk.CTkFont(family="Arial", size=18, weight="bold"),
            text_color="white",
            justify="center",
        ).place(relx=0.54, rely=0.38, anchor="center")

        ctk.CTkLabel(
            footer,
            text="La Masia Team",
            font=ctk.CTkFont(family="Arial", size=18, weight="bold"),
            text_color="white",
        ).place(relx=0.54, rely=0.68, anchor="center")

    def _render_logo(self, canvas: tk.Canvas) -> None:
        image = self._get_logo_image(self.competition.logo_path, max_width=135, max_height=105)
        if image is not None:
            canvas.delete("all")
            canvas.create_image(90, 60, image=image)
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
            scale = max(
                1,
                math.ceil(image.width() / max_width),
                math.ceil(image.height() / max_height),
            )
            if scale > 1:
                image = image.subsample(scale, scale)
            self.logo_images[cache_key] = image
            return image
        except tk.TclError:
            return None

    def _draw_logo_fallback(self, canvas: tk.Canvas) -> None:
        canvas.delete("all")
        if self.competition.key == "ucl":
            canvas.create_oval(60, 6, 150, 96, outline="white", width=3)
            for pts in (
                (104, 6, 115, 22, 132, 24, 120, 36, 124, 54, 106, 44, 88, 52, 92, 34, 78, 24, 96, 22),
                (68, 26, 84, 20, 92, 38, 84, 54, 66, 46),
                (128, 28, 142, 40, 134, 58, 118, 52, 116, 36),
                (82, 58, 96, 52, 108, 66, 98, 84, 80, 76),
                (112, 68, 126, 58, 140, 74, 128, 90, 110, 84),
            ):
                canvas.create_polygon(*pts, fill="white", outline="white")
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
            154,
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
