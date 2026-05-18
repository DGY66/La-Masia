from __future__ import annotations

import re
import unicodedata


ESPN_TEAM_IDS: dict[str, int] = {
    "aberdeen": 256,
    "aek athens": 3828,
    "ajax": 139,
    "arsenal": 359,
    "aston villa": 362,
    "atalanta": 105,
    "atletico madrid": 1068,
    "athletic club": 93,
    "az alkmaar": 132,
    "barcelona": 83,
    "basel": 896,
    "bayer 04 leverkusen": 131,
    "bayern munchen": 132,
    "benfica": 1929,
    "bodo glimt": 608,
    "bologna": 107,
    "borussia dortmund": 124,
    "borussia monchengladbach": 268,
    "braga": 2994,
    "brann": 3183,
    "celtic": 256,
    "celta vigo": 85,
    "chelsea": 363,
    "club brugge": 570,
    "copenhagen": 400,
    "crvena zvezda": 227,
    "crystal palace": 384,
    "dinamo zagreb": 597,
    "dynamo kyiv": 330,
    "eintracht frankfurt": 125,
    "fenerbahce": 436,
    "feyenoord": 142,
    "fiorentina": 109,
    "freiburg": 126,
    "galatasaray": 432,
    "genk": 673,
    "go ahead eagles": 143,
    "inter": 110,
    "juventus": 111,
    "kairat almaty": 5966,
    "lech poznan": 551,
    "legia warszawa": 557,
    "lille": 166,
    "liverpool": 364,
    "ludogorets razgrad": 7752,
    "lyon": 167,
    "maccabi tel aviv": 611,
    "mainz": 2950,
    "malmo": 3644,
    "manchester united": 360,
    "manchester city": 382,
    "marseille": 176,
    "midtjylland": 3416,
    "monaco": 174,
    "napoli": 114,
    "newcastle united": 361,
    "nice": 2502,
    "nottingham forest": 393,
    "olympiacos": 435,
    "paok": 1175,
    "panathinaikos": 443,
    "paris saint germain": 160,
    "porto": 437,
    "psv": 148,
    "rangers": 257,
    "rayo vallecano": 101,
    "real betis": 244,
    "real madrid": 86,
    "red bull salzburg": 2790,
    "roma": 104,
    "sevilla": 243,
    "shakhtar donetsk": 493,
    "slavia praha": 558,
    "sparta praha": 548,
    "sporting cp": 2250,
    "strasbourg": 180,
    "stuttgart": 134,
    "sturm graz": 337,
    "tottenham hotspur": 367,
    "union saint gilloise": 7603,
    "utrecht": 151,
    "valencia": 94,
    "viktoria plzen": 11706,
    "villarreal": 102,
    "young boys": 2722,
}

ALIASES: dict[str, str] = {
    "ac sparta praha": "sparta praha",
    "arsenal fc": "arsenal",
    "as monaco": "monaco",
    "as roma": "roma",
    "aston villa fc": "aston villa",
    "atalanta bc": "atalanta",
    "athletic bilbao": "athletic club",
    "atletico": "atletico madrid",
    "atletico de madrid": "atletico madrid",
    "b dortmund": "borussia dortmund",
    "barca": "barcelona",
    "bayer leverkusen": "bayer 04 leverkusen",
    "bayern munich": "bayern munchen",
    "bodoglimt": "bodo glimt",
    "borussia dortmund gmbh co kgaa": "borussia dortmund",
    "borussia m gladbach": "borussia monchengladbach",
    "borussia mg": "borussia monchengladbach",
    "borussia moenchengladbach": "borussia monchengladbach",
    "borussia monchengladbach": "borussia monchengladbach",
    "borussia mönchengladbach": "borussia monchengladbach",
    "m gladbach": "borussia monchengladbach",
    "monchengladbach": "borussia monchengladbach",
    "moenchengladbach": "borussia monchengladbach",
    "bsc young boys": "young boys",
    "celtic fc": "celtic",
    "celta": "celta vigo",
    "club brugge kv": "club brugge",
    "dynamo kiev": "dynamo kyiv",
    "fc barcelona": "barcelona",
    "fc bayern munchen": "bayern munchen",
    "fc bayern munich": "bayern munchen",
    "fc copenhagen": "copenhagen",
    "fc midtjylland": "midtjylland",
    "fc porto": "porto",
    "fenerbahce sk": "fenerbahce",
    "feyenooord": "feyenoord",
    "florentina": "fiorentina",
    "frankfurt": "eintracht frankfurt",
    "gnk dinamo": "dinamo zagreb",
    "gnk dinamo zagreb": "dinamo zagreb",
    "inter milan": "inter",
    "internazionale": "inter",
    "leverkusen": "bayer 04 leverkusen",
    "liverpool fc": "liverpool",
    "m tel aviv": "maccabi tel aviv",
    "maccabi tel aviv fc": "maccabi tel aviv",
    "malmo ff": "malmo",
    "man united": "manchester united",
    "man utd": "manchester united",
    "manchester utd": "manchester united",
    "manchester united fc": "manchester united",
    "newcastle": "newcastle united",
    "newcastle utd": "newcastle united",
    "nott m forest": "nottingham forest",
    "nottm forest": "nottingham forest",
    "olympiacos piraeus": "olympiacos",
    "olympiakos": "olympiacos",
    "panathinaiko": "panathinaikos",
    "panathinaikos fc": "panathinaikos",
    "paris": "paris saint germain",
    "paris sg": "paris saint germain",
    "psg": "paris saint germain",
    "rb salzburg": "red bull salzburg",
    "rc celta": "celta vigo",
    "real betis balompie": "real betis",
    "real madrid cf": "real madrid",
    "red bull salzburg": "red bull salzburg",
    "royale union saint gilloise": "union saint gilloise",
    "salzburg": "red bull salzburg",
    "sevilla fc": "sevilla",
    "shakhtar": "shakhtar donetsk",
    "sk slavia praha": "slavia praha",
    "sk sturm graz": "sturm graz",
    "slavia prague": "slavia praha",
    "sparta prague": "sparta praha",
    "sporting": "sporting cp",
    "sporting clube de portugal": "sporting cp",
    "sporting lisbon": "sporting cp",
    "storm graz": "sturm graz",
    "tottenham": "tottenham hotspur",
    "tottenham hotspur fc": "tottenham hotspur",
    "union sg": "union saint gilloise",
    "union st gilloise": "union saint gilloise",
    "valencia cf": "valencia",
    "villareal": "villarreal",
    "villarreal cf": "villarreal",
}


def _normalize(text: str) -> str:
    ascii_text = (
        unicodedata.normalize("NFKD", text.casefold())
        .encode("ascii", "ignore")
        .decode("ascii")
    )
    return " ".join(re.sub(r"[^a-z0-9]+", " ", ascii_text).split())


def resolve_espn_id(*team_names: str | None) -> int | None:
    candidates: list[str] = []
    for team_name in team_names:
        if not team_name:
            continue
        normalized = _normalize(team_name)
        if normalized:
            candidates.append(ALIASES.get(normalized, normalized))

    for candidate in candidates:
        direct = ESPN_TEAM_IDS.get(candidate)
        if direct is not None:
            return direct

    for candidate in candidates:
        for key, team_id in ESPN_TEAM_IDS.items():
            if candidate.startswith(key) or key.startswith(candidate):
                return team_id

    return None
