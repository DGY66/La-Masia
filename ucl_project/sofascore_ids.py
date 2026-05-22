from __future__ import annotations

import re
import unicodedata


SOFASCORE_TEAM_IDS: dict[str, int] = {
    "aek athens": 2692,
    "aek larnaca": 3382,
    "breidablik": 2429,
    "az alkmaar": 2950,
    "celje": 2427,
    "crystal palace": 7,
    "dynamo kyiv": 3305,
    "drita": 53015,
    "fc alashkert": 67966,
    "fc lugano": 2443,
    "fc midtjylland": 1289,
    "fiorentina": 2693,
    "hacken": 1892,
    "hamrun spartans": 52050,
    "jagiellonia bialystok": 2788,
    "kaa gent": 2903,
    "kups kuopio": 1921,
    "lausanne sport": 2413,
    "lech poznan": 2185,
    "legia warszawa": 2187,
    "lincoln red imps": 24222,
    "ludogorets": 43840,
    "mainz": 2556,
    "nk celje": 2427,
    "noah": 281033,
    "ssc napoli": 2714,
    "omonia nicosia": 3474,
    "rayo vallecano": 2818,
    "real sociedad": 2824,
    "rijeka": 2546,
    "rakow czestochowa": 60805,
    "rb leipzig": 36360,
    "rapid wien": 2542,
    "samsunspor": 3052,
    "shamrock rovers": 3065,
    "shakhtar donetsk": 3044,
    "shkendija": 2392,
    "sigma olomouc": 2421,
    "slovan bratislava": 2423,
    "sparta praha": 2425,
    "sporting braga": 2999,
    "strasbourg": 1658,
    "universitatea craiova": 2547,
    "vfl wolfsburg": 2524,
    "zrinjski mostar": 2998,
}

ALIASES: dict[str, str] = {
    "ac sparta praha": "sparta praha",
    "az": "az alkmaar",
    "az alkmaar": "az alkmaar",
    "breidablik": "breidablik",
    "brei ablik": "breidablik",
    "alashkert": "fc alashkert",
    "fc lausanne sport": "lausanne sport",
    "fc alashkert": "fc alashkert",
    "fc lugano": "fc lugano",
    "fc midtjylland": "fc midtjylland",
    "fc noah": "noah",
    "fiorentina": "fiorentina",
    "florentina": "fiorentina",
    "gent": "kaa gent",
    "hnk rijeka": "rijeka",
    "jagiellonia": "jagiellonia bialystok",
    "jogiellonia": "jagiellonia bialystok",
    "kaa gent": "kaa gent",
    "kuopion palloseura": "kups kuopio",
    "kups": "kups kuopio",
    "lausanne sport": "lausanne sport",
    "lech poznan": "lech poznan",
    "ludogorets razgrad": "ludogorets",
    "midtjylland": "fc midtjylland",
    "nk celje": "celje",
    "napoli": "ssc napoli",
    "omonia": "omonia nicosia",
    "omonia nicosia": "omonia nicosia",
    "rakow": "rakow czestochowa",
    "rakow czestochowa": "rakow czestochowa",
    "rasenballsport leipzig": "rb leipzig",
    "real sociedad de futbol": "real sociedad",
    "rijeka": "rijeka",
    "samsunspor": "samsunspor",
    "s bratislava": "slovan bratislava",
    "shakhtar": "shakhtar donetsk",
    "shkendija": "shkendija",
    "sigma olomouc": "sigma olomouc",
    "sk rapid": "rapid wien",
    "slovan bratislava": "slovan bratislava",
    "sporting braga": "sporting braga",
    "u craiova": "universitatea craiova",
    "universitatea craiova": "universitatea craiova",
    "wolfsburg": "vfl wolfsburg",
    "zrinjski": "zrinjski mostar",
}


def _normalize(text: str) -> str:
    ascii_text = (
        unicodedata.normalize("NFKD", text.casefold())
        .encode("ascii", "ignore")
        .decode("ascii")
    )
    return " ".join(re.sub(r"[^a-z0-9]+", " ", ascii_text).split())


def resolve_sofascore_id(*team_names: str | None) -> int | None:
    candidates: list[str] = []
    for team_name in team_names:
        if not team_name:
            continue
        normalized = _normalize(team_name)
        if normalized:
            candidates.append(ALIASES.get(normalized, normalized))

    for candidate in candidates:
        direct = SOFASCORE_TEAM_IDS.get(candidate)
        if direct is not None:
            return direct

    for candidate in candidates:
        for key, team_id in SOFASCORE_TEAM_IDS.items():
            if candidate.startswith(key) or key.startswith(candidate):
                return team_id

    return None
