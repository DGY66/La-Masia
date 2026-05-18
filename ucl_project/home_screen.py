from __future__ import annotations

import tkinter as tk
from pathlib import Path
from typing import Callable

import customtkinter as ctk

from i18n import LANGUAGES, SEASONS, get_home_strings

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

BG_TOP = "#3B47A1"
BG_BOT = "#1D147B"
CARD_BG = "#30338E"
CARD_BORD = "#6C72C8"
SEL_BG = "#4B52AA"
SEL_BORD = "#8A91E5"
BTN_GRAD1 = "#159021"
BTN_GRAD2 = "#106C19"
TEXT_W = "#FFFFFF"
TEXT_MUTED = "#D2D1DF"
ASSETS_DIR = Path(__file__).parent / "assets"

LEAGUES = [
    {"key": "ucl", "name": "UEFA Champions League", "short": "UCL", "color1": "#0017C8", "color2": "#00093A", "logo": "img.png"},
    {"key": "uel", "name": "UEFA Europa League", "short": "UEL", "color1": "#E35A12", "color2": "#35190F", "logo": "img_1.png"},
    {"key": "uecl", "name": "UEFA Conference League", "short": "UECL", "color1": "#00EE12", "color2": "#024C0A", "logo": "img_2.png"},
]


def _hex_rgb(color: str) -> tuple[int, int, int]:
    color = color.lstrip("#")
    return int(color[:2], 16), int(color[2:4], 16), int(color[4:], 16)


class _GradFrame(ctk.CTkFrame):
    def __init__(self, master, c1: str, c2: str, vertical: bool = True, **kwargs):
        kwargs.setdefault("corner_radius", 0)
        super().__init__(master, fg_color=c1, **kwargs)
        self._c1 = c1
        self._c2 = c2
        self._vertical = vertical
        self._canvas = tk.Canvas(self, highlightthickness=0, bd=0, bg=c1)
        self._canvas.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.after_idle(lambda: self._canvas.tk.call("lower", self._canvas._w))
        self.bind("<Configure>", self._redraw)

    def _redraw(self, _event=None) -> None:
        width = max(self.winfo_width(), 2)
        height = max(self.winfo_height(), 2)
        self._canvas.configure(width=width, height=height)
        self._canvas.delete("grad")

        r1, g1, b1 = _hex_rgb(self._c1)
        r2, g2, b2 = _hex_rgb(self._c2)
        steps = height if self._vertical else width
        for index in range(steps):
            ratio = index / max(steps - 1, 1)
            r = int(r1 + (r2 - r1) * ratio)
            g = int(g1 + (g2 - g1) * ratio)
            b = int(b1 + (b2 - b1) * ratio)
            color = f"#{r:02x}{g:02x}{b:02x}"
            if self._vertical:
                self._canvas.create_line(0, index, width, index, fill=color, tags="grad")
            else:
                self._canvas.create_line(index, 0, index, height, fill=color, tags="grad")


class _StarCanvas(tk.Canvas):
    def __init__(self, master, **kwargs):
        super().__init__(master, highlightthickness=0, bd=0, **kwargs)
        self._stars: list[tuple[float, float, float, float]] = []
        self._after_id: str | None = None
        self.bind("<Configure>", self._init_stars)
        self.bind("<Destroy>", self._on_destroy)
        self._animate()

    def _init_stars(self, _event=None) -> None:
        import random

        width = max(self.winfo_width(), 800)
        height = max(self.winfo_height(), 600)
        self._stars = [
            (random.uniform(0, width), random.uniform(0, height), random.uniform(0.5, 2.5), random.uniform(0.002, 0.008))
            for _ in range(120)
        ]
        self._draw_stars()

    def _draw_stars(self) -> None:
        self.delete("star")
        for x, y, size, _ in self._stars:
            self.create_oval(x - size, y - size, x + size, y + size, fill="white", outline="", tags="star")

    def _animate(self) -> None:
        if self._stars:
            width = max(self.winfo_width(), 800)
            height = max(self.winfo_height(), 600)
            next_stars = []
            for x, y, size, speed in self._stars:
                next_stars.append(((x + 0.15) % width, (y + speed * 10) % height, size, speed))
            self._stars = next_stars
            self._draw_stars()
        if self.winfo_exists():
            self._after_id = self.after(60, self._animate)

    def _on_destroy(self, _event=None) -> None:
        if self._after_id is not None:
            try:
                self.after_cancel(self._after_id)
            except tk.TclError:
                pass
            self._after_id = None


class HomeScreen(ctk.CTk):
    def __init__(self, on_launch: Callable[[str, str, str], None]) -> None:
        super().__init__()
        self._on_launch = on_launch
        self._selected_season = SEASONS[0]["key"]
        self._selected_league = LEAGUES[0]["key"]
        self._language = "English"
        self._league_cards: dict[str, ctk.CTkFrame] = {}
        self._league_name_labels: dict[str, ctk.CTkLabel] = {}
        self._select_buttons: dict[str, ctk.CTkButton] = {}
        self._logo_images: dict[str, tk.PhotoImage] = {}

        self.title(get_home_strings(self._language)["app_title"])
        self.geometry("1024x720")
        self.minsize(980, 680)
        self.configure(fg_color=BG_TOP)
        self.protocol("WM_DELETE_WINDOW", self._close_window)

        self._build()

    def _build(self) -> None:
        bg = _GradFrame(self, BG_TOP, BG_BOT, vertical=True)
        bg.place(relx=0, rely=0, relwidth=1, relheight=1)

        self._build_top_bar(bg)

        content = ctk.CTkFrame(bg, fg_color="transparent")
        content.place(relx=0.5, rely=0.54, anchor="center", relwidth=0.96)

        self._build_hero(content)
        self._build_league_section(content)

    def _build_top_bar(self, parent) -> None:
        strings = get_home_strings(self._language)
        self._app_title = ctk.CTkLabel(
            parent,
            text=strings["app_title"],
            font=ctk.CTkFont(family="Arial", size=34, weight="bold"),
            text_color=TEXT_W,
        )
        self._app_title.place(x=14, y=16, anchor="nw")

        self._season_menu = ctk.CTkOptionMenu(
            parent,
            values=self._season_values(),
            command=self._pick_season,
            width=360,
            height=36,
            corner_radius=18,
            font=ctk.CTkFont(family="Arial", size=13, weight="bold"),
            fg_color=SEL_BG,
            button_color=SEL_BG,
            button_hover_color=CARD_BORD,
            text_color=TEXT_W,
            dropdown_font=ctk.CTkFont(family="Arial", size=13),
            dropdown_fg_color=SEL_BG,
            dropdown_hover_color=CARD_BORD,
            dropdown_text_color=TEXT_W,
        )
        self._season_menu.set(self._season_display(self._selected_season))
        self._season_menu.place(relx=0.99, y=16, anchor="ne")

        self._lang_menu = ctk.CTkOptionMenu(
            parent,
            values=LANGUAGES,
            command=self._change_language,
            width=116,
            height=36,
            corner_radius=18,
            fg_color=SEL_BG,
            button_color=SEL_BG,
            button_hover_color=CARD_BORD,
            text_color=TEXT_W,
            font=ctk.CTkFont(family="Arial", size=13, weight="bold"),
        )
        self._lang_menu.set(self._language)
        self._lang_menu.place(relx=0.99, y=58, anchor="ne")

    def _build_language_selector(self, parent) -> None:
        self._lang_menu = ctk.CTkOptionMenu(
            parent,
            values=LANGUAGES,
            command=self._change_language,
            width=120,
            fg_color=CARD_BG,
            button_color=SEL_BG,
            button_hover_color=SEL_BORD,
            text_color=TEXT_W,
            font=ctk.CTkFont(family="Arial", size=12),
        )
        self._lang_menu.set(self._language)
        self._lang_menu.place(relx=0.98, rely=0.03, anchor="ne")

    def _build_hero(self, parent) -> None:
        strings = get_home_strings(self._language)
        hero = ctk.CTkFrame(parent, fg_color="transparent")
        hero.pack(pady=(0, 26))

        self._hero_title = ctk.CTkLabel(
            hero,
            text=strings["choose_competition"],
            font=ctk.CTkFont(family="Arial", size=44, weight="bold"),
            text_color=TEXT_W,
        )
        self._hero_title.pack()

        self._hero_sub = ctk.CTkLabel(
            hero,
            text=strings["choose_subtitle"],
            font=ctk.CTkFont(family="Arial", size=26, weight="bold"),
            text_color=TEXT_MUTED,
        )
        self._hero_sub.pack(pady=(4, 0))

    def _build_season_section(self, parent) -> None:
        strings = get_home_strings(self._language)
        wrap = ctk.CTkFrame(parent, fg_color="transparent")
        wrap.pack(fill="x", pady=(0, 24))

        self._season_lbl = ctk.CTkLabel(
            wrap,
            text=strings["season"],
            font=ctk.CTkFont(family="Arial", size=11, weight="bold"),
            text_color=TEXT_MUTED,
        )
        self._season_lbl.pack(anchor="center", pady=(0, 10))

        self._season_menu = ctk.CTkOptionMenu(
            wrap,
            values=self._season_values(),
            command=self._pick_season,
            width=260,
            height=44,
            corner_radius=22,
            font=ctk.CTkFont(family="Arial", size=13, weight="bold"),
            fg_color=CARD_BG,
            button_color=SEL_BG,
            button_hover_color=SEL_BORD,
            text_color=TEXT_W,
            dropdown_font=ctk.CTkFont(family="Arial", size=13),
            dropdown_fg_color=CARD_BG,
            dropdown_hover_color=SEL_BG,
            dropdown_text_color=TEXT_W,
        )
        self._season_menu.pack()
        self._season_menu.set(self._season_display(self._selected_season))

    def _build_league_section(self, parent) -> None:
        wrap = ctk.CTkFrame(parent, fg_color="transparent")
        wrap.pack(fill="x")

        cards_row = ctk.CTkFrame(wrap, fg_color="transparent")
        cards_row.pack()

        for league in LEAGUES:
            card = self._make_league_card(cards_row, league)
            card.pack(side="left", padx=12)
            self._league_cards[league["key"]] = card

    def _make_league_card(self, parent, league: dict[str, str]) -> ctk.CTkFrame:
        is_selected = league["key"] == self._selected_league
        card = ctk.CTkFrame(
            parent,
            width=310,
            height=245,
            corner_radius=14,
            fg_color=SEL_BG if is_selected else CARD_BG,
            border_color=SEL_BORD if is_selected else CARD_BORD,
            border_width=1,
        )
        card.pack_propagate(False)

        inner = _GradFrame(card, league["color1"], league["color2"], vertical=False, corner_radius=14)
        inner.pack(expand=True, fill="both")

        logo = self._get_logo_image(str(league["logo"]), max_width=92, max_height=92)
        if logo is not None:
            logo_label = ctk.CTkLabel(inner, text="", image=logo)
            logo_label.image = logo
            logo_label.pack(pady=(18, 10))

        name_label = ctk.CTkLabel(
            inner,
            text=self._league_name(league["key"]).upper(),
            font=ctk.CTkFont(family="Arial", size=24, weight="bold"),
            text_color=TEXT_W,
            wraplength=270,
            justify="center",
        )
        name_label.pack(expand=True)
        self._league_name_labels[league["key"]] = name_label

        select_btn = ctk.CTkButton(
            inner,
            text=str(get_home_strings(self._language)["select"]),
            width=98,
            height=30,
            corner_radius=7,
            fg_color=BTN_GRAD1,
            hover_color=BTN_GRAD2,
            text_color=TEXT_W,
            font=ctk.CTkFont(family="Arial", size=17, weight="bold"),
            command=lambda key=league["key"]: self._launch_league(key),
        )
        select_btn.pack(pady=(0, 34))
        self._select_buttons[league["key"]] = select_btn

        for widget in [card, inner, *inner.winfo_children()]:
            widget.bind("<Button-1>", lambda _e, key=league["key"]: self._pick_league(key))
        for widget in [card, inner]:
            widget.bind("<Enter>", lambda _e, w=card, key=league["key"]: self._card_hover(w, key, True))
            widget.bind("<Leave>", lambda _e, w=card, key=league["key"]: self._card_hover(w, key, False))

        return card

    def _build_launch_btn(self, parent) -> None:
        strings = get_home_strings(self._language)
        wrap = ctk.CTkFrame(parent, fg_color="transparent")
        wrap.pack(pady=(0, 12))

        self._launch_btn = ctk.CTkButton(
            wrap,
            text=strings["view_standings"],
            width=280,
            height=54,
            corner_radius=27,
            font=ctk.CTkFont(family="Arial", size=15, weight="bold"),
            fg_color=BTN_GRAD1,
            hover_color=BTN_GRAD2,
            text_color="white",
            command=self._launch,
        )
        self._launch_btn.pack()

        self._launch_info = ctk.CTkLabel(
            wrap,
            text=self._launch_label(),
            font=ctk.CTkFont(family="Arial", size=12),
            text_color=TEXT_MUTED,
        )
        self._launch_info.pack(pady=(8, 0))

    def _season_values(self) -> list[str]:
        return [self._season_display(season["key"]) for season in SEASONS]

    def _season_display(self, season_key: str) -> str:
        strings = get_home_strings(self._language)
        season = next(item for item in SEASONS if item["key"] == season_key)
        return f"{season['label']}  ·  {strings[season['tag_key']]}"

    def _change_language(self, language: str) -> None:
        self._language = language
        strings = get_home_strings(self._language)
        self.title(strings["app_title"])
        self._app_title.configure(text=strings["app_title"])
        self._hero_title.configure(text=strings["choose_competition"])
        self._hero_sub.configure(text=strings["choose_subtitle"])
        for league_key, label in self._league_name_labels.items():
            label.configure(text=self._league_name(league_key).upper())
        for button in self._select_buttons.values():
            button.configure(text=strings["select"])
        self._season_menu.configure(values=self._season_values())
        self._season_menu.set(self._season_display(self._selected_season))

    def _pick_season(self, display_value: str) -> None:
        for season in SEASONS:
            if self._season_display(season["key"]) == display_value:
                self._selected_season = season["key"]
                break
        self._refresh_info()

    def _pick_league(self, key: str) -> None:
        self._selected_league = key
        for league_key, card in self._league_cards.items():
            selected = league_key == key
            card.configure(
                fg_color=SEL_BG if selected else CARD_BG,
                border_color=SEL_BORD if selected else CARD_BORD,
            )
        self._refresh_info()

    def _card_hover(self, card: ctk.CTkFrame, key: str, entering: bool) -> None:
        if key == self._selected_league:
            return
        card.configure(fg_color=SEL_BG if entering else CARD_BG)

    def _launch_label(self) -> str:
        season_display = self._season_display(self._selected_season)
        league_name = next(league["short"] for league in LEAGUES if league["key"] == self._selected_league)
        return f"{league_name}  ·  {season_display}"

    def _league_name(self, league_key: str) -> str:
        strings = get_home_strings(self._language)
        competitions = strings.get("competitions", {})
        fallback = next(league["name"] for league in LEAGUES if league["key"] == league_key)
        return competitions.get(league_key, fallback) if isinstance(competitions, dict) else fallback

    def _refresh_info(self) -> None:
        if hasattr(self, "_launch_info"):
            self._launch_info.configure(text=self._launch_label())

    def _launch_league(self, key: str) -> None:
        self._selected_league = key
        self._launch()

    def _get_logo_image(self, filename: str, max_width: int, max_height: int) -> tk.PhotoImage | None:
        cache_key = f"{filename}:{max_width}x{max_height}"
        if cache_key in self._logo_images:
            return self._logo_images[cache_key]
        path = ASSETS_DIR / filename
        if not path.exists():
            return None
        try:
            image = tk.PhotoImage(file=str(path))
            width_scale = max(1, image.width() // max_width)
            height_scale = max(1, image.height() // max_height)
            scale = max(width_scale, height_scale)
            if scale > 1:
                image = image.subsample(scale, scale)
            self._logo_images[cache_key] = image
            return image
        except tk.TclError:
            return None

    def _launch(self) -> None:
        self._close_window()
        self._on_launch(self._selected_league, self._selected_season, self._language)

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
