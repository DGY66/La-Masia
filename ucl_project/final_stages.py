from __future__ import annotations

import tkinter as tk
from pathlib import Path

import customtkinter as ctk

from config import COMPETITIONS, CompetitionConfig
from espn_logos import ESPNLogoManager
from espn_ids import resolve_espn_id
from i18n import get_table_strings


FINAL_STAGE_DATA: dict[str, dict[str, object]] = {
    "ucl": {
        "title": "UEFA Champions League Winner",
        "date": "01/06/25",
        "home": "PARIS",
        "away": "INTER",
        "home_score": 5,
        "away_score": 0,
        "home_id": resolve_espn_id("Paris Saint Germain"),
        "away_id": resolve_espn_id("Inter"),
    },
    "uel": {
        "title": "UEFA Europa League Winner",
        "date": "22/05/25",
        "home": "SPURS",
        "away": "MAN. UTD",
        "home_score": 1,
        "away_score": 0,
        "home_id": resolve_espn_id("Tottenham Hotspur"),
        "away_id": resolve_espn_id("Manchester United"),
    },
    "uecl": {
        "title": "UEFA Conference League Winner",
        "date": "29/05/25",
        "home": "CHELSEA",
        "away": "REAL BETIS",
        "home_score": 4,
        "away_score": 1,
        "home_id": resolve_espn_id("Chelsea"),
        "away_id": resolve_espn_id("Real Betis"),
    },
}


class FinalStagesWindow(ctk.CTkToplevel):
    def __init__(self, master: ctk.CTk, competition_key: str, language: str = "English") -> None:
        super().__init__(master)
        self.competition: CompetitionConfig = COMPETITIONS[competition_key]
        self.data = FINAL_STAGE_DATA[competition_key]
        self.strings = get_table_strings(language)
        self.logo_manager = ESPNLogoManager()
        self.logo_placeholder = self.logo_manager.get_placeholder((64, 64))
        self.bg_image: tk.PhotoImage | None = None
        self.match_canvas: tk.Canvas | None = None
        self.title(str(self.data["title"]))
        self.geometry("1024x720")
        self.minsize(900, 620)
        self.configure(fg_color=self.competition.header_gradient[0])
        self.protocol("WM_DELETE_WINDOW", self._close)
        self.logo_manager.start_ui_pump(self)
        self._build()
        self.transient(master)
        self.lift()
        self.focus_force()

    def _build(self) -> None:
        self.canvas = tk.Canvas(self, highlightthickness=0, bd=0, bg=self.competition.header_gradient[0])
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<Configure>", self._redraw_background)

        close_btn = ctk.CTkButton(
            self,
            text=str(self.strings["back"]),
            command=self._close,
            width=88,
            height=34,
            corner_radius=16,
            fg_color="#FFFFFF",
            text_color="#101010",
            hover_color="#EAEAEA",
            font=ctk.CTkFont(family="Arial", size=13, weight="bold"),
        )
        close_btn.place(x=42, y=18)

        title = ctk.CTkLabel(
            self,
            text=str(self.data["title"]),
            font=ctk.CTkFont(family="Arial", size=36, weight="bold"),
            text_color="white",
        )
        title.place(x=42, y=82)

        ctk.CTkLabel(
            self,
            text=str(self.strings["matches"]),
            font=ctk.CTkFont(family="Arial", size=18, weight="bold"),
            text_color="white",
        ).place(x=180, y=150)

        self._build_controls()
        self._build_match()

    def _build_controls(self) -> None:
        group = ctk.CTkFrame(self, fg_color="white", width=250, height=40, corner_radius=20)
        group.place(x=92, y=194)
        group.pack_propagate(False)

        date_btn = ctk.CTkButton(
            group,
            text=str(self.strings["by_date"]),
            command=lambda: None,
            font=ctk.CTkFont(family="Arial", size=16),
            fg_color="white",
            hover_color="#EDEDED",
            text_color="#101010",
            width=125,
            height=36,
            corner_radius=18,
        )
        date_btn.pack(side="left", padx=2, pady=2)

        round_btn = ctk.CTkButton(
            group,
            text=str(self.strings["by_round"]),
            command=lambda: None,
            font=ctk.CTkFont(family="Arial", size=16),
            fg_color="#050505",
            hover_color="#202020",
            text_color="white",
            width=121,
            height=36,
            corner_radius=18,
        )
        round_btn.pack(side="right", padx=2, pady=2)

        self.round_menu = ctk.CTkOptionMenu(
            self,
            values=[str(self.strings["final"])],
            width=132,
            height=40,
            corner_radius=8,
            fg_color=self.competition.header_gradient[0],
            button_color="#FFFFFF",
            button_hover_color="#EDEDED",
            text_color="white",
            dropdown_fg_color="#FFFFFF",
            dropdown_text_color="#101010",
            dropdown_hover_color="#EDEDED",
            font=ctk.CTkFont(family="Arial", size=17),
        )
        self.round_menu.set(str(self.strings["final"]))
        self.round_menu.place(x=156, y=240)

    def _close(self) -> None:
        master = self.master
        if hasattr(master, "final_stages_window"):
            master.final_stages_window = None
        self.destroy()

    def _build_match(self) -> None:
        self.match_canvas = tk.Canvas(self, width=650, height=190, highlightthickness=0, bd=0, bg=self.competition.header_gradient[0])
        self.match_canvas.place(x=26, y=278)
        self.match_canvas.create_line(116, 0, 116, 160, fill="#E4E4E4", width=3)
        self.match_canvas.create_line(134, 78, 620, 78, fill="#E4E4E4", width=2)

        self.match_canvas.create_text(
            52,
            68,
            text=f"{self.data['date']}\nFT",
            fill="#C7C7C7",
            font=("Arial", 21, "bold"),
            justify="center",
        )

        self._place_team(284, str(self.data["home"]), int(self.data["home_score"]), self.data.get("home_id"))
        self._place_team(374, str(self.data["away"]), int(self.data["away_score"]), self.data.get("away_id"))

    def _place_team(self, y: int, name: str, score: int, team_id: object) -> None:
        label = ctk.CTkLabel(self, text="", image=self.logo_placeholder, fg_color="transparent")
        label.image = self.logo_placeholder
        label.place(x=180, y=y, anchor="nw")
        if isinstance(team_id, int):
            self.logo_manager.load_logo_async(
                team_id,
                (64, 64),
                lambda image, target=label: self._set_logo(target, image),
            )

        ctk.CTkLabel(
            self,
            text=name,
            font=ctk.CTkFont(family="Arial", size=30, weight="bold"),
            text_color="white",
        ).place(x=252, y=y + 32, anchor="w")

        ctk.CTkLabel(
            self,
            text=str(score),
            font=ctk.CTkFont(family="Arial", size=30, weight="bold"),
            text_color="white",
        ).place(x=624, y=y + 32, anchor="w")

    def _set_logo(self, label: ctk.CTkLabel, image: ctk.CTkImage) -> None:
        if label.winfo_exists():
            label.configure(image=image)
            label.image = image

    def _redraw_background(self, event: tk.Event) -> None:
        width = max(event.width, 2)
        height = max(event.height, 2)
        self.canvas.delete("bg")
        c1, c2 = self.competition.header_gradient
        r1, g1, b1 = self._hex_to_rgb(c1)
        r2, g2, b2 = self._hex_to_rgb(c2)
        for x in range(width):
            ratio = x / max(width - 1, 1)
            color = f"#{int(r1 + (r2 - r1) * ratio):02x}{int(g1 + (g2 - g1) * ratio):02x}{int(b1 + (b2 - b1) * ratio):02x}"
            self.canvas.create_line(x, 0, x, height, fill=color, tags="bg")
        self._draw_background_logo(width, height)
        self.canvas.tag_lower("bg")
        if self.match_canvas is not None:
            self.match_canvas.configure(bg=self.competition.header_gradient[0])

    def _draw_background_logo(self, width: int, height: int) -> None:
        logo_path = Path(self.competition.logo_path)
        if not logo_path.exists():
            return
        try:
            self.bg_image = tk.PhotoImage(file=str(logo_path))
        except tk.TclError:
            return
        self.canvas.create_image(width // 2 - 70, height // 2 + 30, image=self.bg_image, tags="bg")

    @staticmethod
    def _hex_to_rgb(color: str) -> tuple[int, int, int]:
        color = color.lstrip("#")
        return int(color[0:2], 16), int(color[2:4], 16), int(color[4:6], 16)
