
from __future__ import annotations

from typing import Literal


FormResult = Literal["W", "D", "L"]


class Team:
    __slots__ = (
        "team_id",
        "abbr",
        "name",
        "country_name",
        "country_alpha2",
        "espn_id",
        "transfermarkt_id",
        "team_logo_url",
        "country_flag_url",
        "pld",
        "w",
        "d",
        "l",
        "gf",
        "ga",
        "form",
        "_pts_override",
    )

    def __init__(
        self,
        abbr: str,
        name: str,
        team_id: int | None = None,
        country_name: str | None = None,
        country_alpha2: str | None = None,
        espn_id: int | None = None,
        transfermarkt_id: int | None = None,
    ) -> None:
        self.team_id: int | None = team_id
        self.abbr: str = abbr
        self.name: str = name
        self.country_name: str | None = country_name
        self.country_alpha2: str | None = country_alpha2.upper() if country_alpha2 else None
        self.espn_id: int | None = espn_id
        self.transfermarkt_id: int | None = transfermarkt_id
        self.team_logo_url: str | None = (
            f"https://img.sofascore.com/api/v1/team/{team_id}/image" if team_id else None
        )
        self.country_flag_url: str | None = self._build_country_flag_url(self.country_alpha2)
        self.pld: int = 0
        self.w: int = 0
        self.d: int = 0
        self.l: int = 0
        self.gf: int = 0
        self.ga: int = 0
        self.form: list[FormResult] = []
        self._pts_override: int | None = None

    @staticmethod
    def _build_country_flag_url(country_alpha2: str | None) -> str | None:
        if not country_alpha2:
            return None
        special_codes = {
            "EN": "gb-eng",
            "SCT": "gb-sct",
            "WAL": "gb-wls",
            "NIR": "gb-nir",
            "XK": "xk",
        }
        key = special_codes.get(country_alpha2.upper(), country_alpha2.lower())
        return f"https://flagcdn.com/w40/{key}.png"

    @property
    def flag_emoji(self) -> str:
        if not self.country_alpha2 or len(self.country_alpha2) != 2 or not self.country_alpha2.isalpha():
            return ""
        return "".join(chr(127397 + ord(letter)) for letter in self.country_alpha2.upper())

    @property
    def gd(self) -> int:
        return self.gf - self.ga

    @property
    def pts(self) -> int:
        if self._pts_override is not None:
            return self._pts_override
        return self.w * 3 + self.d

    @pts.setter
    def pts(self, value: int) -> None:
        self._pts_override = value

    def sort_key(self) -> tuple[int, int, int]:
        return (-self.pts, -self.gd, -self.gf)

    def __repr__(self) -> str:
        return f"Team({self.abbr!r}, {self.name!r}, pts={self.pts}, gd={self.gd})"
