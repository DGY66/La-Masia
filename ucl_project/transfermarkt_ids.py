from __future__ import annotations

import unicodedata


TRANSFERMARKT_TEAM_IDS: dict[str, int] = {
    "arsenal": 11,
    "aston villa": 405,
    "atalanta": 800,
    "atletico madrid": 13_718,
    "barcelona": 131,
    "bayer 04 leverkusen": 15,
    "bayern munchen": 27,
    "benfica": 294,
    "borussia dortmund": 16,
    "bodo glimt": 2619,
    "bologna": 1025,
    "celtic": 371,
    "chelsea": 631,
    "club brugge": 2282,
    "copenhagen": 190,
    "dinamo zagreb": 419,
    "eintracht frankfurt": 24,
    "fenerbahce": 36,
    "feyenoord": 234,
    "galatasaray": 141,
    "girona": 12321,
    "inter": 46,
    "juventus": 506,
    "lazio": 398,
    "lille": 1082,
    "liverpool": 31,
    "manchester city": 281,
    "monaco": 162,
    "napoli": 6195,
    "newcastle united": 762,
    "paris saint germain": 583,
    "psg": 583,
    "porto": 720,
    "psv": 383,
    "real madrid": 418,
    "rb leipzig": 23826,
    "real sociedad": 681,
    "roma": 12,
    "salzburg": 409,
    "shakhtar donetsk": 660,
    "slavia praha": 324,
    "sporting braga": 1075,
    "sporting cp": 336,
    "sporting": 336,
    "stade brestois 29": 3911,
    "tottenham hotspur": 148,
    "union saint gilloise": 3709,
    "young boys": 452,
}

ALIASES: dict[str, str] = {
    "arsenal fc": "arsenal",
    "aston villa fc": "aston villa",
    "atalanta bc": "atalanta",
    "atl madrid": "atletico madrid",
    "atletico": "atletico madrid",
    "atletico de madrid": "atletico madrid",
    "bayern": "bayern munchen",
    "fc barcelona": "barcelona",
    "barca": "barcelona",
    "fc bayern munchen": "bayern munchen",
    "fc bayern munich": "bayern munchen",
    "fc bayern munchen ii": "bayern munchen",
    "bayern munich": "bayern munchen",
    "bayern munchen": "bayern munchen",
    "borussia dortmund": "borussia dortmund",
    "b dortmund": "borussia dortmund",
    "dortmund": "borussia dortmund",
    "club brugge kv": "club brugge",
    "frankfurt": "eintracht frankfurt",
    "internazionale": "inter",
    "inter milan": "inter",
    "juventus turin": "juventus",
    "leverkusen": "bayer 04 leverkusen",
    "liverpool fc": "liverpool",
    "losc lille": "lille",
    "man city": "manchester city",
    "manchester city fc": "manchester city",
    "newcastle": "newcastle united",
    "newcastle utd": "newcastle united",
    "paris": "paris saint germain",
    "paris sg": "paris saint germain",
    "paris saint germain": "paris saint germain",
    "psg": "paris saint germain",
    "real madrid cf": "real madrid",
    "rasenballsport leipzig": "rb leipzig",
    "red bull salzburg": "salzburg",
    "spurs": "tottenham hotspur",
    "sporting clube de portugal": "sporting cp",
    "sporting braga": "sporting braga",
    "sporting lisbon": "sporting cp",
    "ssc napoli": "napoli",
    "tottenham": "tottenham hotspur",
    "tottenham hotspur fc": "tottenham hotspur",
    "union sg": "union saint gilloise",
}


def _normalize(text: str) -> str:
    return " ".join(
        unicodedata.normalize("NFKD", text.casefold())
        .encode("ascii", "ignore")
        .decode("ascii")
        .replace(".", " ")
        .replace("-", " ")
        .replace("/", " ")
        .split()
    )


def resolve_transfermarkt_id(team_name: str) -> int | None:
    normalized = _normalize(team_name)
    canonical = ALIASES.get(normalized, normalized)

    direct = TRANSFERMARKT_TEAM_IDS.get(canonical)
    if direct is not None:
        return direct

    for key, team_id in TRANSFERMARKT_TEAM_IDS.items():
        if canonical.startswith(key) or key.startswith(canonical):
            return team_id

    return None
