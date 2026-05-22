from __future__ import annotations

import csv
import logging
import tkinter as tk
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from tkinter import filedialog, messagebox
from typing import Any

import customtkinter as ctk

from config import COMPETITIONS, CompetitionConfig
from espn_ids import resolve_espn_id
from i18n import SEASONS, get_competition_title, get_table_strings
from models import Team
from team_logos import get_best_team_logo
from transfermarkt_ids import resolve_transfermarkt_id


logger = logging.getLogger(__name__)

BASE_W = 1440
LAYOUT_W = 1024
LAYOUT_H = 720
MIN_UI_SCALE = 0.78
MAX_UI_SCALE = 1.0
OLD_UECL_SEASONS = {"1516", "1617", "1718", "1819", "1920", "2021"}

LINE_COLOR = "#E8E8F6"


@dataclass(frozen=True)
class KnockoutTeam:
    name: str
    short_name: str
    sofascore_id: int | None
    country: str | None = None
    winner: bool = False


@dataclass(frozen=True)
class KnockoutMatch:
    home: KnockoutTeam
    away: KnockoutTeam
    home_score: str
    away_score: str
    date: str = ""
    note: str = ""
    finished: bool = False
    order: int = 0


@dataclass(frozen=True)
class KnockoutRound:
    key: str
    name: str
    order: int
    matches: tuple[KnockoutMatch, ...]


def _fallback_team(name: str) -> KnockoutTeam:
    return KnockoutTeam(name=name, short_name=name, sofascore_id=None)


def _fallback_match(
    home: str,
    away: str,
    home_score: int | str | None,
    away_score: int | str | None,
    date: str = "",
    note: str = "",
) -> KnockoutMatch:
    return KnockoutMatch(
        home=_fallback_team(home),
        away=_fallback_team(away),
        home_score="-" if home_score is None else str(home_score),
        away_score="-" if away_score is None else str(away_score),
        date=date,
        note=note,
        finished=home_score is not None and away_score is not None,
    )


COMMON_2425_ROUNDS: tuple[KnockoutRound, ...] = (
    KnockoutRound(
        key="quarterfinals",
        name="Quarterfinals",
        order=1,
        matches=(
            _fallback_match("Real Madrid", "Arsenal", 1, 5),
            _fallback_match("PSG", "Aston Villa", 5, 4),
            _fallback_match("Barcelona", "Dortmund", 5, 3),
            _fallback_match("Bayern", "Inter", 3, 4),
        ),
    ),
    KnockoutRound(
        key="semifinals",
        name="Semifinals",
        order=2,
        matches=(
            _fallback_match("Arsenal", "PSG", 1, 3),
            _fallback_match("Barcelona", "Inter", 6, 7),
        ),
    ),
    KnockoutRound(
        key="final",
        name="Final",
        order=3,
        matches=(_fallback_match("Inter", "PSG", 0, 5),),
    ),
)


UEL_2425_ROUNDS: tuple[KnockoutRound, ...] = (
    KnockoutRound(
        key="quarterfinals",
        name="Quarterfinals",
        order=1,
        matches=(
            _fallback_match("Tottenham", "Frankfurt", 2, 1),
            _fallback_match("Lazio", "Bode/Glimt", "3 (3)", "3 (2)"),
            _fallback_match("Rangers", "Athletic Club", 0, 2),
            _fallback_match("Lyon", "MAN UTD.", 6, 7),
        ),
    ),
    KnockoutRound(
        key="semifinals",
        name="Semifinals",
        order=2,
        matches=(
            _fallback_match("Bode/Glimt", "Tottenham", 1, 5),
            _fallback_match("Athletic Club", "MAN UTD.", 1, 7),
        ),
    ),
    KnockoutRound(
        key="final",
        name="Final",
        order=3,
        matches=(_fallback_match("MAN UTD.", "Tottenham", 0, 1),),
    ),
)


UECL_2425_ROUNDS: tuple[KnockoutRound, ...] = (
    KnockoutRound(
        key="quarterfinals",
        name="Quarterfinals",
        order=1,
        matches=(
            _fallback_match("Jagiellonia", "Real Betis", 1, 3),
            _fallback_match("Fiorentina", "Celje", 4, 3),
            _fallback_match("Chelsea", "Legia", 4, 2),
            _fallback_match("Djurgårdens", "Rapid", 4, 2),
        ),
    ),
    KnockoutRound(
        key="semifinals",
        name="Semifinals",
        order=2,
        matches=(
            _fallback_match("Fiorentina", "Real Betis", 3, 4),
            _fallback_match("Djurgårdens", "Chelsea", 1, 5),
        ),
    ),
    KnockoutRound(
        key="final",
        name="Final",
        order=3,
        matches=(_fallback_match("Real Betis", "Chelsea", 1, 4),),
    ),
)


FALLBACK_FINALS: dict[str, dict[str, KnockoutMatch]] = {
    "ucl": {
        "1516": _fallback_match("Real Madrid", "Atletico", 1, 1, "28/05/16", "5-3 pens"),
        "1617": _fallback_match("Real Madrid", "Juventus", 4, 1, "03/06/17"),
        "1718": _fallback_match("Real Madrid", "Liverpool", 3, 1, "26/05/18"),
        "1819": _fallback_match("Liverpool", "Spurs", 2, 0, "01/06/19"),
        "1920": _fallback_match("Bayern", "Paris", 1, 0, "23/08/20"),
        "2021": _fallback_match("Chelsea", "Man. City", 1, 0, "29/05/21"),
        "2122": _fallback_match("Real Madrid", "Liverpool", 1, 0, "28/05/22"),
        "2223": _fallback_match("Man. City", "Inter", 1, 0, "10/06/23"),
        "2324": _fallback_match("Real Madrid", "Dortmund", 2, 0, "01/06/24"),
        "2425": _fallback_match("Paris", "Inter", 5, 0, "01/06/25"),
        "2526": _fallback_match("Paris", "Arsenal", None, None, "30/05/26"),
    },
    "uel": {
        "1516": _fallback_match("Sevilla", "Liverpool", 3, 1, "18/05/16"),
        "1617": _fallback_match("Man. Utd", "Ajax", 2, 0, "24/05/17"),
        "1718": _fallback_match("Atletico", "Marseille", 3, 0, "16/05/18"),
        "1819": _fallback_match("Chelsea", "Arsenal", 4, 1, "29/05/19"),
        "1920": _fallback_match("Sevilla", "Inter", 3, 2, "21/08/20"),
        "2021": _fallback_match("Villarreal", "Man. Utd", 1, 1, "26/05/21", "11-10 pens"),
        "2122": _fallback_match("Frankfurt", "Rangers", 1, 1, "18/05/22", "5-4 pens"),
        "2223": _fallback_match("Sevilla", "Roma", 1, 1, "31/05/23", "4-1 pens"),
        "2324": _fallback_match("Atalanta", "Leverkusen", 3, 0, "22/05/24"),
        "2425": _fallback_match("Tottenham", "Man. Utd", 1, 0, "22/05/25"),
        "2526": _fallback_match("Aston Villa", "Freiburg", 3, 0, "20/05/26"),
    },
    "uecl": {
        "2122": _fallback_match("Roma", "Feyenoord", 1, 0, "25/05/22"),
        "2223": _fallback_match("West Ham", "Fiorentina", 2, 1, "07/06/23"),
        "2324": _fallback_match("Olympiacos", "Fiorentina", 1, 0, "29/05/24", "AET"),
        "2425": _fallback_match("Chelsea", "Real Betis", 4, 1, "29/05/25"),
        "2526": _fallback_match("Crystal Palace", "Rayo Vallecano", None, None, "27/05/26"),
    },
}


class KnockoutDataProvider:
    def get_knockout_data(self, tournament: str, season: str) -> dict[str, object]:
        if tournament == "uecl" and season in OLD_UECL_SEASONS:
            return {
                "status": "not_started",
                "tournament": tournament,
                "season": season,
                "rounds": [],
                "final": None,
                "source": "rule",
            }

        competition = COMPETITIONS[tournament]
        try:
            data = self._from_sofascore(competition, season)
            if data["rounds"]:
                return data
        except Exception as exc:
            logger.warning("Knockout data fallback for %s %s: %s", tournament, season, exc)

        return self._fallback_data(tournament, season)

    def _from_sofascore(self, competition: CompetitionConfig, season: str) -> dict[str, object]:
        from api import SofaScoreApiClient

        client = SofaScoreApiClient()
        season_id = client._resolve_season_candidates(competition, season)[0]
        payload = client._request(
            f"/unique-tournament/{competition.tournament_id}/season/{season_id}/cuptrees"
        )
        cup_trees = payload.get("cupTrees")
        if not isinstance(cup_trees, list) or not cup_trees:
            raise ValueError("cupTrees payload is empty")

        tree = self._pick_cup_tree(cup_trees)
        rounds = self._parse_rounds(tree.get("rounds"))
        final = self._find_final(rounds)
        return {
            "status": "ok",
            "tournament": competition.key,
            "season": season,
            "season_id": season_id,
            "title": f"{competition.title} Winner",
            "rounds": rounds,
            "final": final,
            "source": "sofascore",
        }

    @staticmethod
    def _pick_cup_tree(cup_trees: list[object]) -> dict[str, Any]:
        dict_trees = [item for item in cup_trees if isinstance(item, dict)]
        knockout = [
            item
            for item in dict_trees
            if "knockout" in str(item.get("name", "")).lower()
            or "knockout" in str(item.get("tournament", {}).get("name", "")).lower()
        ]
        return knockout[0] if knockout else dict_trees[0]

    def _parse_rounds(self, raw_rounds: object) -> tuple[KnockoutRound, ...]:
        if not isinstance(raw_rounds, list):
            return ()

        parsed: list[KnockoutRound] = []
        for raw_round in raw_rounds:
            if not isinstance(raw_round, dict):
                continue
            blocks = raw_round.get("blocks")
            if not isinstance(blocks, list):
                continue
            matches = tuple(
                match
                for match in (self._parse_block(block) for block in sorted(blocks, key=lambda item: _safe_int(item.get("order")) if isinstance(item, dict) else 0))
                if match is not None
            )
            if not matches:
                continue
            name = str(raw_round.get("description") or raw_round.get("name") or f"Round {len(parsed) + 1}")
            order = _safe_int(raw_round.get("order"), len(parsed) + 1)
            parsed.append(
                KnockoutRound(
                    key=_round_key(name, order),
                    name=name,
                    order=order,
                    matches=matches,
                )
            )

        return tuple(sorted(parsed, key=lambda item: item.order))

    def _parse_block(self, block: dict[str, Any]) -> KnockoutMatch | None:
        participants = block.get("participants")
        if not isinstance(participants, list) or len(participants) < 2:
            return None
        ordered = sorted(
            (item for item in participants if isinstance(item, dict)),
            key=lambda item: _safe_int(item.get("order"), 99),
        )
        if len(ordered) < 2:
            return None

        home = self._parse_participant(ordered[0])
        away = self._parse_participant(ordered[1])
        home_score = _score(block.get("homeTeamScore"))
        away_score = _score(block.get("awayTeamScore"))
        return KnockoutMatch(
            home=home,
            away=away,
            home_score=home_score,
            away_score=away_score,
            date=_format_timestamp(block.get("seriesStartDateTimestamp")),
            note=self._note(block),
            finished=bool(block.get("finished")),
            order=_safe_int(block.get("order"), 0),
        )

    @staticmethod
    def _parse_participant(participant: dict[str, Any]) -> KnockoutTeam:
        team = participant.get("team")
        if not isinstance(team, dict):
            return _fallback_team("TBD")
        name = str(team.get("shortName") or team.get("name") or "TBD")
        full_name = str(team.get("name") or name)
        team_id = _safe_int(team.get("id"), 0) or None
        country = None
        country_payload = team.get("country")
        if isinstance(country_payload, dict):
            raw_country = country_payload.get("name")
            country = str(raw_country) if raw_country else None
        return KnockoutTeam(
            name=full_name,
            short_name=name,
            sofascore_id=team_id,
            country=country,
            winner=bool(participant.get("winner")),
        )

    @staticmethod
    def _note(block: dict[str, Any]) -> str:
        result = str(block.get("result") or "")
        if result and ":" not in result and "won" not in result.lower():
            return result
        return ""

    @staticmethod
    def _find_final(rounds: tuple[KnockoutRound, ...]) -> KnockoutMatch | None:
        if not rounds:
            return None
        final_round = next((item for item in reversed(rounds) if "final" in item.name.lower()), rounds[-1])
        return final_round.matches[0] if final_round.matches else None

    @staticmethod
    def _fallback_data(tournament: str, season: str) -> dict[str, object]:
        final = FALLBACK_FINALS.get(tournament, {}).get(season)
        rounds: tuple[KnockoutRound, ...] = ()
        if season == "2425" and final is not None:
            if tournament == "ucl":
                rounds = COMMON_2425_ROUNDS
            elif tournament == "uel":
                rounds = UEL_2425_ROUNDS
            elif tournament == "uecl":
                rounds = UECL_2425_ROUNDS
        if final is not None and not rounds:
            rounds = (KnockoutRound("final", "Final", 1, (final,)),)
        return {
            "status": "ok" if final is not None else "empty",
            "tournament": tournament,
            "season": season,
            "rounds": rounds,
            "final": final,
            "source": "local",
        }


class FinalStagesWindow(ctk.CTkToplevel):
    def __init__(
        self,
        master: ctk.CTk,
        competition_key: str,
        season_key: str = "2526",
        language: str = "English",
    ) -> None:
        super().__init__(master)
        self.competition: CompetitionConfig = COMPETITIONS[competition_key]
        self.season_key = season_key
        self.language = language
        self.strings = get_table_strings(language)
        self.provider = KnockoutDataProvider()
        self.data = self.provider.get_knockout_data(competition_key, season_key)
        self.view_mode = "round"
        self.selected_round = "All"
        self._ui_scale = 1.0
        self._widgets: list[tk.Widget] = []
        self._images: list[object] = []
        self._box_centers: dict[tuple[int, int], tuple[float, float]] = {}

        self.title(self._window_title())
        self.geometry("1440x900")
        self.minsize(1040, 720)
        self.configure(fg_color=self._theme()["bg1"])
        self.protocol("WM_DELETE_WINDOW", self._close)
        self.attributes("-fullscreen", True)
        self.bind("<Escape>", lambda _event: self.attributes("-fullscreen", False))

        self.canvas = tk.Canvas(self, highlightthickness=0, bd=0, bg=self._theme()["bg1"])
        self.v_scroll = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.h_scroll = tk.Scrollbar(self, orient="horizontal", command=self.canvas.xview)
        self.canvas.configure(yscrollcommand=self.v_scroll.set, xscrollcommand=self.h_scroll.set)
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.v_scroll.grid(row=0, column=1, sticky="ns")
        self.h_scroll.grid(row=1, column=0, sticky="ew")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.canvas.bind("<Configure>", self._redraw)
        self.transient(master)
        self.lift()
        self.focus_force()

    def _window_title(self) -> str:
        season = self._season_label()
        title = get_competition_title(self.language, self.competition.key, self.competition.title)
        return f"{title} Winner - {season}"

    def _redraw(self, _event: object | None = None) -> None:
        width = max(self.canvas.winfo_width(), 2)
        height = max(self.canvas.winfo_height(), 2)
        self._ui_scale = max(MIN_UI_SCALE, min(width / LAYOUT_W, height / LAYOUT_H, MAX_UI_SCALE))
        self.canvas.delete("all")
        self._clear_widgets()
        self._draw_background(width, height)
        self._draw_header(width)
        self._draw_controls()

        status = self.data.get("status")
        if status == "not_started":
            self._draw_message(self._text("uecl_not_started", "Tournament did not exist this season"))
            self.canvas.configure(scrollregion=(0, 0, width, height))
            return
        if status == "empty":
            self._draw_message(self._text("no_knockout_data", "Knockout data is not available for this season."))
            self.canvas.configure(scrollregion=(0, 0, width, height))
            return

        if self.view_mode == "date":
            content_w, content_h = self._draw_by_date(width)
        else:
            content_w, content_h = self._draw_by_round(width)
        self.canvas.configure(scrollregion=(0, 0, max(width, content_w), max(height, content_h)))

    def _clear_widgets(self) -> None:
        for widget in self._widgets:
            if widget.winfo_exists():
                widget.destroy()
        self._widgets.clear()
        self._images.clear()
        self._box_centers.clear()

    def _draw_background(self, width: int, height: int) -> None:
        theme = self._theme()
        self.canvas.configure(bg=theme["bg1"])
        r1, g1, b1 = _hex_to_rgb(theme["bg1"])
        r2, g2, b2 = _hex_to_rgb(theme["bg2"])
        for x in range(width):
            ratio = x / max(width - 1, 1)
            color = f"#{int(r1 + (r2 - r1) * ratio):02x}{int(g1 + (g2 - g1) * ratio):02x}{int(b1 + (b2 - b1) * ratio):02x}"
            self.canvas.create_line(x, 0, x, height, fill=color, tags="background")
        self._draw_background_logo(width, height)

    def _draw_background_logo(self, width: int, height: int) -> None:
        path = Path(self.competition.logo_path)
        if not path.exists():
            return
        try:
            from PIL import Image, ImageTk

            image = Image.open(path).convert("RGBA")
            target = int(min(width, height) * (0.72 if self.competition.key == "ucl" else 0.68))
            ratio = target / max(image.size)
            resized = image.resize(
                (max(1, int(image.width * ratio)), max(1, int(image.height * ratio))),
                Image.Resampling.LANCZOS,
            )
            alpha = resized.getchannel("A").point(lambda value: int(value * self._theme()["logo_alpha"]))
            resized.putalpha(alpha)
            photo = ImageTk.PhotoImage(resized)
        except Exception:
            return
        self._images.append(photo)
        self.canvas.create_image(width * 0.42, height * 0.54, image=photo, tags="background")

    def _draw_header(self, width: int) -> None:
        title = get_competition_title(self.language, self.competition.key, self.competition.title)
        self.canvas.create_text(
            self._x(122),
            self._y(28),
            text=f"{title} Winner",
            fill="white",
            font=("Arial", self._font(30), "bold italic"),
            anchor="nw",
        )
        self.canvas.create_text(
            width - self._x(40),
            self._y(38),
            text=self._season_label(),
            fill="white",
            font=("Arial", self._font(12), "bold"),
            anchor="ne",
        )
        source = str(self.data.get("source") or "")
        if source:
            self.canvas.create_text(
                width - self._x(40),
                self._y(58),
                text=source.upper(),
                fill="#DDE4FF",
                font=("Arial", self._font(9), "bold"),
                anchor="ne",
            )

    def _draw_controls(self) -> None:
        back = self._make_button(
            self._text("back", "Back"),
            self._close,
            fg="#FFFFFF",
            text_color="#101010",
            width=max(72, int(78 * self._ui_scale)),
            height=max(24, int(28 * self._ui_scale)),
        )
        self.canvas.create_window(self._x(42), self._y(30), window=back, anchor="nw")

        by_date = self._make_button(
            self._text("by_date", "By date"),
            lambda: self._set_mode("date"),
            fg="#FFFFFF" if self.view_mode == "round" else "#050505",
            text_color="#111111" if self.view_mode == "round" else "#FFFFFF",
            width=max(118, int(150 * self._ui_scale)),
            height=max(30, int(38 * self._ui_scale)),
        )
        by_round = self._make_button(
            self._text("by_round", "By round"),
            lambda: self._set_mode("round"),
            fg="#050505" if self.view_mode == "round" else "#FFFFFF",
            text_color="#FFFFFF" if self.view_mode == "round" else "#111111",
            width=max(118, int(150 * self._ui_scale)),
            height=max(30, int(38 * self._ui_scale)),
        )
        self.canvas.create_window(self._x(42), self._y(82), window=by_date, anchor="nw")
        self.canvas.create_window(self._x(164), self._y(82), window=by_round, anchor="nw")

        if self.view_mode == "round":
            round_values = [self._text("final", "Final")]
            round_menu = ctk.CTkOptionMenu(
                self.canvas,
                values=round_values,
                command=self._select_round,
                width=max(120, int(128 * self._ui_scale)),
                height=max(34, int(38 * self._ui_scale)),
                corner_radius=max(7, int(8 * self._ui_scale)),
                fg_color=self._theme()["box"],
                button_color="#FFFFFF",
                button_hover_color="#EDEDED",
                text_color="#FFFFFF",
                dropdown_fg_color="#17258D",
                dropdown_text_color="#FFFFFF",
                font=ctk.CTkFont(family="Arial", size=self._font(15), weight="bold"),
            )
            round_menu.set(round_values[0])
            self._widgets.append(round_menu)
            self.canvas.create_window(self._x(98), self._y(128), window=round_menu, anchor="nw")

        export = self._make_button("Export", self._export_csv, fg=self._theme()["export"], text_color="#FFFFFF", width=max(58, int(56 * self._ui_scale)), height=max(20, int(22 * self._ui_scale)))
        self.canvas.create_window(self._x(884), self._y(30), window=export, anchor="nw")

    def _make_button(self, label_text: str, command, fg: str, text_color: str, width: int, height: int) -> ctk.CTkButton:
        button = ctk.CTkButton(
            self.canvas,
            text=label_text,
            command=command,
            width=width,
            height=height,
            corner_radius=height // 2,
            fg_color=fg,
            hover_color="#2B2B2B" if fg == "#050505" else "#EDEDED",
            text_color=text_color,
            font=ctk.CTkFont(family="Arial", size=self._font(12), weight="bold"),
        )
        self._widgets.append(button)
        return button

    def _set_mode(self, mode: str) -> None:
        self.view_mode = mode
        self._redraw()

    def _select_round(self, value: str) -> None:
        self.selected_round = value
        self.view_mode = "round"
        self._redraw()

    def _draw_by_round(self, width: int) -> tuple[int, int]:
        rounds = self._reference_rounds()
        if not rounds:
            self._draw_message(self._text("no_knockout_data", "Knockout data is not available for this season."))
            return width, 760

        final = self.data.get("final")
        if isinstance(final, KnockoutMatch):
            self._draw_feature_final(final)

        box_w = self._x(270)
        box_h = self._y(62)
        x_positions = [self._x(64), self._x(388), self._x(710)]
        title_y = self._y(290)
        base_positions = {
            0: [self._y(325), self._y(400), self._y(475), self._y(550)],
            1: [self._y(363), self._y(513)],
            2: [self._y(439)],
        }
        content_h = self._y(705)
        content_w = self._x(1010)

        centers_by_round: list[list[tuple[float, float]]] = []
        for round_index, round_item in enumerate(rounds):
            x = x_positions[min(round_index, len(x_positions) - 1)]
            if not self._is_final_round(round_item.name):
                self.canvas.create_text(
                    x + box_w / 2,
                    title_y,
                    text=self._round_name(round_item.name),
                    fill="white",
                    font=("Arial", self._font(17), "bold"),
                    anchor="center",
                )
            centers: list[tuple[float, float]] = []
            for match_index, match in enumerate(round_item.matches):
                y_values = base_positions.get(round_index, [])
                if match_index < len(y_values):
                    y = y_values[match_index]
                else:
                    y = self._y(300 + match_index * 76)
                center = self._draw_match_box(x, y, box_w, box_h, match, small=True)
                centers.append(center)
                self._box_centers[(round_index, match_index)] = center
            centers_by_round.append(centers)

        self._draw_connectors(rounds, centers_by_round, box_w, 0)

        if centers_by_round and centers_by_round[-1]:
            fc = centers_by_round[-1][0]
            label_cx = fc[0] - box_w / 2
            label_top = fc[1] + box_h / 2 + self._y(6)
            lw, lh = self._x(60), self._y(22)
            self._round_rect(
                label_cx - lw / 2, label_top,
                label_cx + lw / 2, label_top + lh,
                lh / 2, "#E8A800", "#E8A800", 1,
            )
            self.canvas.create_text(
                label_cx, label_top + lh / 2,
                text=self._text("final", "Final"),
                fill="#FFFFFF",
                font=("Arial", self._font(10), "bold"),
                anchor="center",
            )

        return int(content_w), int(content_h)

    def _draw_connectors(
        self,
        rounds: tuple[KnockoutRound, ...],
        centers_by_round: list[list[tuple[float, float]]],
        box_w: int,
        col_gap: int,
    ) -> None:
        for round_index in range(len(rounds) - 1):
            current = centers_by_round[round_index]
            nxt = centers_by_round[round_index + 1]
            if not current or not nxt:
                continue
            for match_index, (_, y1) in enumerate(current):
                next_index = min(match_index // max(1, len(current) // max(1, len(nxt))), len(nxt) - 1)
                x1 = current[match_index][0]
                x2 = nxt[next_index][0] - box_w
                y2 = nxt[next_index][1]
                mid = x1 + (x2 - x1) * 0.55
                self.canvas.create_line(x1, y1, mid, y1, mid, y2, x2, y2, fill=LINE_COLOR, width=max(2, int(2 * self._ui_scale)))

    def _draw_by_date(self, width: int) -> tuple[int, int]:
        matches: list[tuple[str, str, KnockoutMatch]] = []
        for round_item in self._all_rounds():
            for match in round_item.matches:
                matches.append((match.date or "TBD", self._round_name(round_item.name), match))
        matches.sort(key=lambda item: item[0])

        y = self._y(205)
        label_x = self._x(42)
        date_x = self._x(180)
        box_x = self._x(222)
        box_w = self._x(430)
        box_h = self._y(58)
        row_gap = self._y(68)
        self.canvas.create_text(
            label_x,
            y - self._y(32),
            text=self._text("matches", "Matches"),
            fill="white",
            font=("Arial", self._font(18), "bold"),
            anchor="w",
        )
        for _, round_name, match in matches:
            self.canvas.create_text(
                label_x,
                y + box_h / 2,
                text=round_name,
                fill="#DDE4FF",
                font=("Arial", self._font(11), "bold"),
                anchor="w",
                width=max(90, date_x - label_x - self._x(14)),
            )
            self._draw_match_box(box_x, y, box_w, box_h, match, small=True)
            if match.date:
                self.canvas.create_text(
                    date_x,
                    y + box_h / 2,
                    text=f"{match.date}\nFT",
                    fill="#D7D7D7",
                    font=("Arial", self._font(10), "bold"),
                    justify="center",
                    anchor="e",
                )
            y += row_gap
        return max(width, int(box_x + box_w + self._x(42))), int(y + self._y(36))

    def _draw_feature_final(self, match: KnockoutMatch) -> None:
        x = self._x(132)
        y = self._y(188)
        self.canvas.create_line(x, y, x, y + self._y(82), fill="#E8E8E8", width=max(3, int(3 * self._ui_scale)))
        self.canvas.create_line(x + self._x(18), y + self._y(41), x + self._x(250), y + self._y(41), fill="#E8E8E8", width=max(2, int(2 * self._ui_scale)))
        self.canvas.create_text(
            x - self._x(20),
            y + self._y(42),
            text=f"{match.date or ''}\nFT",
            fill="#D7D7D7",
            font=("Arial", self._font(13), "bold"),
            justify="center",
            anchor="e",
        )
        self._draw_team_line(match.home, match.home_score, x + self._x(36), y + self._y(22), x + self._x(250), False, large=True)
        self._draw_team_line(match.away, match.away_score, x + self._x(36), y + self._y(67), x + self._x(250), False, large=True)

    def _draw_match_box(self, x: float, y: float, w: float, h: float, match: KnockoutMatch, small: bool) -> tuple[float, float]:
        theme = self._theme()
        self._round_rect(x, y, x + w, y + h, max(8, int(8 * self._ui_scale)), theme["box"], "#FFFFFF", max(2, int(2 * self._ui_scale)))
        home_winner = match.home.winner or _winner_from_score(match.home_score, match.away_score, True)
        away_winner = match.away.winner or _winner_from_score(match.home_score, match.away_score, False)
        self._draw_team_line(match.home, match.home_score, x + 18, y + h * 0.30, x + w - 18, not home_winner, large=not small)
        self._draw_team_line(match.away, match.away_score, x + 18, y + h * 0.72, x + w - 18, not away_winner, large=not small)
        return x + w, y + h / 2

    def _draw_team_line(
        self,
        team: KnockoutTeam,
        score: str,
        x: float,
        y: float,
        score_x: float,
        muted: bool,
        large: bool,
    ) -> None:
        color = "#AAB0CF" if muted else "#FFFFFF"
        size = max(15, int((32 if large else 17) * self._ui_scale))
        text_size = self._font(18 if large else 11)
        score_size = self._font(20 if large else 11)
        weight = "bold" if large else "normal"
        max_name_width = max(70, score_x - x - size - self._x(36))
        label = team.short_name.upper() if large else team.short_name
        label = self._fit_label(label, text_size, max_name_width)
        self._place_logo(team, x, y - size / 2, size)
        self.canvas.create_text(
            x + size + 12,
            y,
            text=label,
            fill=color,
            font=("Arial", text_size, weight),
            anchor="w",
        )
        self.canvas.create_text(
            score_x,
            y,
            text=score,
            fill=color,
            font=("Arial", score_size, "bold"),
            anchor="e",
        )

    @staticmethod
    def _fit_label(text: str, font_size: int, max_width: float) -> str:
        avg_char_width = max(5.0, font_size * 0.58)
        max_chars = max(4, int(max_width / avg_char_width))
        if len(text) <= max_chars:
            return text
        return text[: max(1, max_chars - 3)].rstrip() + "..."

    def _place_logo(self, team: KnockoutTeam, x: float, y: float, size: int) -> None:
        logo_team = Team(
            abbr=(team.short_name or team.name or "??")[:3].upper(),
            name=team.name,
            team_id=team.sofascore_id,
            espn_id=resolve_espn_id(team.name),
            transfermarkt_id=resolve_transfermarkt_id(team.name),
        )
        image = get_best_team_logo(logo_team, (size, size))
        label = ctk.CTkLabel(self.canvas, text="", image=image, fg_color="transparent", width=size, height=size)
        label.image = image
        self._widgets.append(label)
        self.canvas.create_window(x, y, window=label, anchor="nw")

    def _draw_message(self, text: str) -> None:
        self.canvas.create_text(
            BASE_W / 2,
            430,
            text=text,
            fill="white",
            font=("Arial", 28, "bold"),
            justify="center",
            anchor="center",
            width=880,
        )

    def _round_values(self) -> list[str]:
        values = ["All"]
        values.extend(self._round_name(round_item.name) for round_item in self._all_rounds())
        return values

    def _reference_rounds(self) -> tuple[KnockoutRound, ...]:
        rounds = list(self._all_rounds())
        selected: list[KnockoutRound] = []
        for wanted in ("quarter", "semi", "final"):
            match = next((item for item in rounds if self._is_round(item.name, wanted)), None)
            if match is not None:
                selected.append(match)
        if len(selected) >= 3:
            return tuple(selected[-3:])
        if len(rounds) >= 3:
            return tuple(rounds[-3:])
        return tuple(rounds)

    @staticmethod
    def _is_round(name: str, wanted: str) -> bool:
        normalized = _round_key(name, 0)
        if wanted == "final":
            return "final" in normalized and "quarter" not in normalized and "semi" not in normalized
        return wanted in normalized

    def _is_final_round(self, name: str) -> bool:
        return self._is_round(name, "final")

    def _visible_rounds(self) -> tuple[KnockoutRound, ...]:
        rounds = self._all_rounds()
        if self.selected_round == "All":
            return rounds
        return tuple(round_item for round_item in rounds if self._round_name(round_item.name) == self.selected_round)

    def _all_rounds(self) -> tuple[KnockoutRound, ...]:
        rounds = self.data.get("rounds")
        return rounds if isinstance(rounds, tuple) else ()

    def _export_csv(self) -> None:
        path = filedialog.asksaveasfilename(
            parent=self,
            defaultextension=".csv",
            initialfile=f"{self.competition.short_title}_{self.season_key}_knockout.csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
        )
        if not path:
            return
        rows = [["round", "date", "home", "home_score", "away", "away_score", "note"]]
        for round_item in self._all_rounds():
            for match in round_item.matches:
                rows.append([
                    self._round_name(round_item.name),
                    match.date,
                    match.home.name,
                    match.home_score,
                    match.away.name,
                    match.away_score,
                    match.note,
                ])
        try:
            with open(path, "w", newline="", encoding="utf-8-sig") as file:
                csv.writer(file).writerows(rows)
        except OSError as exc:
            messagebox.showerror("Export failed", str(exc), parent=self)

    def _round_name(self, name: str) -> str:
        normalized = _round_key(name, 0)
        if "quarter" in normalized:
            return self._text("quarterfinals", "Quarterfinals")
        if "semi" in normalized:
            return self._text("semifinals", "Semifinals")
        if "final" in normalized and "semi" not in normalized:
            return self._text("final", "Final")
        if "16" in normalized or "18" in normalized:
            return "Round of 16"
        if "playoff" in normalized or "play" in normalized:
            return "Play-off"
        return name

    def _text(self, key: str, fallback: str) -> str:
        value = self.strings.get(key)
        return str(value) if isinstance(value, str) else fallback

    def _season_label(self) -> str:
        return next((item["label"].replace(" / ", "/") for item in SEASONS if item["key"] == self.season_key), self.season_key)

    def _theme(self) -> dict[str, Any]:
        if self.competition.key == "ucl":
            return {"bg1": "#15057A", "bg2": "#AAB0DC", "box": "#2A347F", "export": "#2637A9", "logo_alpha": 0.24}
        if self.competition.key == "uel":
            return {"bg1": "#130D10", "bg2": "#E04B05", "box": "#D55B00", "export": "#8C4219", "logo_alpha": 0.36}
        return {"bg1": "#032912", "bg2": "#00BE15", "box": "#13A500", "export": "#078B18", "logo_alpha": 0.34}

    def _x(self, value: float) -> float:
        return value * self._ui_scale

    def _y(self, value: float) -> float:
        return value * self._ui_scale

    def _font(self, value: int) -> int:
        return max(8, int(value * self._ui_scale))

    def _round_rect(self, x1: float, y1: float, x2: float, y2: float, radius: float, fill: str, outline: str, width: int) -> None:
        points = [
            x1 + radius, y1, x2 - radius, y1, x2, y1, x2, y1 + radius,
            x2, y2 - radius, x2, y2, x2 - radius, y2, x1 + radius, y2,
            x1, y2, x1, y2 - radius, x1, y1 + radius, x1, y1,
        ]
        self.canvas.create_polygon(points, smooth=True, fill=fill, outline=outline, width=width)

    def _close(self) -> None:
        master = self.master
        if hasattr(master, "final_stages_window"):
            master.final_stages_window = None
        self.destroy()


def _safe_int(value: object, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _score(value: object) -> str:
    if value in (None, ""):
        return "-"
    return str(value)


def _format_timestamp(value: object) -> str:
    timestamp = _safe_int(value, 0)
    if timestamp <= 0:
        return ""
    return datetime.fromtimestamp(timestamp).strftime("%d/%m/%y")


def _round_key(name: str, order: int) -> str:
    cleaned = "".join(ch.lower() if ch.isalnum() else "_" for ch in name)
    return f"{order}_{cleaned.strip('_')}"


def _winner_from_score(home_score: str, away_score: str, home: bool) -> bool:
    try:
        home_value = int(home_score.split()[0])
        away_value = int(away_score.split()[0])
    except (ValueError, IndexError):
        return False
    return home_value >= away_value if home else away_value >= home_value


def _hex_to_rgb(color: str) -> tuple[int, int, int]:
    color = color.lstrip("#")
    return int(color[0:2], 16), int(color[2:4], 16), int(color[4:6], 16)
