
from __future__ import annotations

from typing import Literal


FormResult = Literal["W", "D", "L"]


class Team:
    __slots__ = ("abbr", "name", "pld", "w", "d", "l", "gf", "ga", "form", "_pts_override")

    def __init__(self, abbr: str, name: str) -> None:
        self.abbr: str = abbr
        self.name: str = name
        self.pld: int = 0
        self.w: int = 0
        self.d: int = 0
        self.l: int = 0
        self.gf: int = 0
        self.ga: int = 0
        self.form: list[FormResult] = []
        self._pts_override: int | None = None

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