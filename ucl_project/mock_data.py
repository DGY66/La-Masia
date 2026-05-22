from __future__ import annotations

from espn_ids import resolve_espn_id
from models import Team
from transfermarkt_ids import resolve_transfermarkt_id


def _build_teams(rows: list[tuple[str, str, int, int, int, int, int, int, int, list[str]]]) -> list[Team]:
    teams: list[Team] = []
    for abbr, name, pld, w, d, l, gf, ga, pts, form in rows:
        team = Team(
            abbr,
            name,
            espn_id=resolve_espn_id(name),
            transfermarkt_id=resolve_transfermarkt_id(name),
        )
        team.pld = pld
        team.w = w
        team.d = d
        team.l = l
        team.gf = gf
        team.ga = ga
        team.pts = pts
        team.form = form
        teams.append(team)
    return teams


def get_mock_teams(competition_key: str) -> list[Team]:
    if competition_key == "uel":
        return _build_teams(_UEL_MOCK_DATA)
    if competition_key == "uecl":
        return _build_teams(_UECL_MOCK_DATA)
    return _build_teams(_UCL_MOCK_DATA)


_UCL_MOCK_DATA = [
    ("AR", "Arsenal Fc", 0, 0, 0, 0, 0, 0, 0, ["W", "W", "W", "W", "W"]),
    ("BM", "Bayern München", 0, 0, 0, 0, 0, 0, 0, ["W", "L", "W", "W", "W"]),
    ("LP", "Liverpool", 0, 0, 0, 0, 0, 0, 0, ["W", "L", "W", "W", "W"]),
    ("TH", "Tottenham", 0, 0, 0, 0, 0, 0, 0, ["W", "L", "W", "W", "W"]),
    ("BL", "Barcelona", 0, 0, 0, 0, 0, 0, 0, ["D", "L", "W", "W", "W"]),
    ("CH", "Chelsea", 0, 0, 0, 0, 0, 0, 0, ["D", "L", "W", "W", "W"]),
    ("SP", "Sporting CP", 0, 0, 0, 0, 0, 0, 0, ["D", "L", "W", "W", "W"]),
    ("MC", "Manchester City", 0, 0, 0, 0, 0, 0, 0, ["W", "L", "W", "L", "W"]),
    ("RM", "Real Madrid", 0, 0, 0, 0, 0, 0, 0, ["L", "W", "L", "W", "L"]),
    ("IN", "Inter", 0, 0, 0, 0, 0, 0, 0, ["W", "L", "L", "L", "W"]),
    ("PS", "Paris", 0, 0, 0, 0, 0, 0, 0, ["L", "W", "D", "L", "D"]),
    ("NC", "Newcastle", 0, 0, 0, 0, 0, 0, 0, ["W", "L", "D", "W", "D"]),
    ("JU", "Juventus", 0, 0, 0, 0, 0, 0, 0, ["D", "W", "W", "W", "D"]),
    ("AL", "Atletico", 0, 0, 0, 0, 0, 0, 0, ["W", "W", "W", "D", "L"]),
    ("CH", "Atalanta", 0, 0, 0, 0, 0, 0, 0, ["W", "W", "W", "L", "L"]),
    ("LK", "Leverkusen", 0, 0, 0, 0, 0, 0, 0, ["W", "W", "D", "L", "W"]),
    ("DM", "B.Dortmund", 0, 0, 0, 0, 0, 0, 0, ["L", "W", "D", "L", "L"]),
    ("OM", "Olympiacos", 0, 0, 0, 0, 0, 0, 0, ["D", "L", "W", "W", "W"]),
    ("PS", "Club Brugge", 0, 0, 0, 0, 0, 0, 0, ["D", "L", "L", "W", "W"]),
    ("GL", "Galatasaray", 0, 0, 0, 0, 0, 0, 0, ["W", "L", "L", "D", "L"]),
    ("MO", "Monaco", 0, 0, 0, 0, 0, 0, 0, ["W", "D", "W", "L", "D"]),
    ("QA", "Qarabağ", 0, 0, 0, 0, 0, 0, 0, ["D", "L", "L", "W", "L"]),
    ("BO", "Bodø/Glimt", 0, 0, 0, 0, 0, 0, 0, ["L", "L", "D", "W", "W"]),
    ("BE", "Benfica", 0, 0, 0, 0, 0, 0, 0, ["L", "W", "W", "L", "W"]),
    ("MA", "Marseille", 0, 0, 0, 0, 0, 0, 0, ["L", "W", "W", "L", "L"]),
    ("PA", "Pafos", 0, 0, 0, 0, 0, 0, 0, ["W", "D", "L", "L", "W"]),
    ("UN", "Union SG", 0, 0, 0, 0, 0, 0, 0, ["L", "W", "L", "L", "W"]),
    ("PV", "PSV", 0, 0, 0, 0, 0, 0, 0, ["D", "W", "L", "L", "L"]),
    ("AC", "Athletic Club", 0, 0, 0, 0, 0, 0, 0, ["L", "D", "D", "W", "L"]),
    ("NA", "Napoli", 0, 0, 0, 0, 0, 0, 0, ["D", "W", "L", "D", "L"]),
    ("CO", "Copenhagen", 0, 0, 0, 0, 0, 0, 0, ["L", "W", "W", "D", "W"]),
    ("AJ", "Ajax", 0, 0, 0, 0, 0, 0, 0, ["L", "L", "W", "W", "L"]),
    ("FR", "Frankfurt", 0, 0, 0, 0, 0, 0, 0, ["D", "L", "L", "L", "L"]),
    ("SL", "Slavia Praha", 0, 0, 0, 0, 0, 0, 0, ["L", "D", "L", "L", "L"]),
    ("VL", "Villareal", 0, 0, 0, 0, 0, 0, 0, ["L", "L", "L", "L", "L"]),
    ("KA", "Kairat Almaty", 0, 0, 0, 0, 0, 0, 0, ["L", "L", "L", "L", "L"]),
]

_UEL_MOCK_DATA = [
    ("LY", "Lyon", 0, 0, 0, 0, 0, 0, 0, ["W", "W", "W", "W", "W"]),
    ("AV", "Aston Villa", 0, 0, 0, 0, 0, 0, 0, ["W", "L", "W", "W", "W"]),
    ("MD", "Midtjylland", 0, 0, 0, 0, 0, 0, 0, ["W", "L", "W", "W", "W"]),
    ("RB", "Real Betis", 0, 0, 0, 0, 0, 0, 0, ["W", "L", "W", "W", "W"]),
    ("PR", "Porto", 0, 0, 0, 0, 0, 0, 0, ["D", "L", "W", "W", "W"]),
    ("BR", "Braga", 0, 0, 0, 0, 0, 0, 0, ["D", "L", "W", "W", "W"]),
    ("FR", "Freiburg", 0, 0, 0, 0, 0, 0, 0, ["D", "L", "W", "W", "W"]),
    ("RO", "Roma", 0, 0, 0, 0, 0, 0, 0, ["W", "L", "W", "L", "W"]),
    ("GN", "Genk", 0, 0, 0, 0, 0, 0, 0, ["L", "W", "L", "W", "L"]),
    ("BL", "Bologna", 0, 0, 0, 0, 0, 0, 0, ["W", "L", "L", "L", "W"]),
    ("ST", "Stuttgart", 0, 0, 0, 0, 0, 0, 0, ["L", "W", "D", "L", "D"]),
    ("FR", "Ferencváros", 0, 0, 0, 0, 0, 0, 0, ["W", "L", "D", "W", "D"]),
    ("NT", "Nott'm Forest", 0, 0, 0, 0, 0, 0, 0, ["D", "W", "W", "W", "D"]),
    ("VP", "Viktoria Plzeň", 0, 0, 0, 0, 0, 0, 0, ["W", "W", "W", "D", "L"]),
    ("CZ", "Crvena Zvezda", 0, 0, 0, 0, 0, 0, 0, ["W", "W", "W", "L", "L"]),
    ("CE", "Celta", 0, 0, 0, 0, 0, 0, 0, ["W", "W", "D", "L", "W"]),
    ("PA", "PAOK", 0, 0, 0, 0, 0, 0, 0, ["L", "W", "D", "L", "L"]),
    ("LI", "Lille", 0, 0, 0, 0, 0, 0, 0, ["D", "L", "W", "W", "W"]),
    ("FE", "Fenerbahçe", 0, 0, 0, 0, 0, 0, 0, ["D", "L", "L", "W", "W"]),
    ("PA", "Panathinaiko", 0, 0, 0, 0, 0, 0, 0, ["W", "L", "L", "D", "L"]),
    ("CE", "Celtic", 0, 0, 0, 0, 0, 0, 0, ["W", "D", "W", "L", "D"]),
    ("LU", "Ludogorets", 0, 0, 0, 0, 0, 0, 0, ["D", "L", "L", "W", "L"]),
    ("GN", "GNK DInamo", 0, 0, 0, 0, 0, 0, 0, ["L", "L", "D", "W", "W"]),
    ("BR", "Brann", 0, 0, 0, 0, 0, 0, 0, ["L", "W", "W", "L", "W"]),
    ("YB", "Young Boys", 0, 0, 0, 0, 0, 0, 0, ["L", "W", "W", "L", "L"]),
    ("SG", "Storm Graz", 0, 0, 0, 0, 0, 0, 0, ["W", "D", "L", "L", "W"]),
    ("FC", "FCSB", 0, 0, 0, 0, 0, 0, 0, ["L", "W", "L", "L", "W"]),
    ("GO", "Go Ahead Eagles", 0, 0, 0, 0, 0, 0, 0, ["D", "W", "L", "L", "L"]),
    ("AC", "Feyenooord", 0, 0, 0, 0, 0, 0, 0, ["L", "D", "D", "W", "L"]),
    ("BA", "Basel", 0, 0, 0, 0, 0, 0, 0, ["D", "W", "L", "D", "L"]),
    ("SA", "Salzburg", 0, 0, 0, 0, 0, 0, 0, ["L", "W", "W", "D", "W"]),
    ("RA", "Rangers", 0, 0, 0, 0, 0, 0, 0, ["L", "L", "W", "W", "L"]),
    ("NI", "Nice", 0, 0, 0, 0, 0, 0, 0, ["D", "L", "L", "L", "L"]),
    ("SL", "Utrecht", 0, 0, 0, 0, 0, 0, 0, ["L", "D", "L", "L", "L"]),
    ("MA", "Malmo", 0, 0, 0, 0, 0, 0, 0, ["L", "L", "L", "L", "L"]),
    ("TA", "M.Tel-Aviv", 0, 0, 0, 0, 0, 0, 0, ["L", "L", "L", "L", "L"]),
]

_UECL_MOCK_DATA = [
    ("ST", "Strasbourg", 6, 5, 0, 1, 12, 5, 15, ["W", "W", "W", "W", "W"]),
    ("RA", "Raków", 6, 4, 1, 1, 10, 5, 13, ["W", "L", "W", "W", "W"]),
    ("SP", "Sparta Praha", 6, 4, 1, 1, 10, 6, 13, ["W", "L", "W", "W", "W"]),
    ("AT", "AEK Athens", 6, 4, 1, 1, 9, 5, 13, ["W", "L", "W", "W", "W"]),
    ("RV", "Rayo Vallecano", 6, 3, 2, 1, 8, 5, 11, ["D", "L", "W", "W", "W"]),
    ("SH", "Shakhtar", 6, 3, 2, 1, 8, 6, 11, ["D", "L", "W", "W", "W"]),
    ("MA", "Mainz", 6, 3, 2, 1, 8, 6, 11, ["D", "L", "W", "W", "W"]),
    ("LA", "AEK Larnaca", 6, 3, 1, 2, 7, 6, 10, ["W", "L", "W", "L", "W"]),
    ("LS", "Lausanne Sport", 0, 0, 0, 0, 0, 0, 0, ["L", "W", "L", "W", "L"]),
    ("CR", "Crystal Palace", 0, 0, 0, 0, 0, 0, 0, ["W", "L", "L", "L", "W"]),
    ("LP", "Lech Poznań", 0, 0, 0, 0, 0, 0, 0, ["L", "W", "D", "L", "D"]),
    ("SA", "Samsunspor", 0, 0, 0, 0, 0, 0, 0, ["W", "L", "D", "W", "D"]),
    ("CE", "Celije", 0, 0, 0, 0, 0, 0, 0, ["D", "W", "W", "W", "D"]),
    ("AZ", "AZ Alkmaar", 0, 0, 0, 0, 0, 0, 0, ["W", "W", "W", "D", "L"]),
    ("FL", "Florentina", 0, 0, 0, 0, 0, 0, 0, ["W", "W", "W", "L", "L"]),
    ("RI", "Rijeka", 0, 0, 0, 0, 0, 0, 0, ["W", "W", "D", "L", "W"]),
    ("JO", "Jogiellonia", 0, 0, 0, 0, 0, 0, 0, ["L", "W", "D", "L", "L"]),
    ("OM", "Omonoia", 0, 0, 0, 0, 0, 0, 0, ["D", "L", "W", "W", "W"]),
    ("NO", "Noah", 0, 0, 0, 0, 0, 0, 0, ["D", "L", "L", "W", "W"]),
    ("DR", "Drita", 0, 0, 0, 0, 0, 0, 0, ["W", "L", "L", "D", "L"]),
    ("KU", "KuPS Kuopio", 0, 0, 0, 0, 0, 0, 0, ["W", "D", "W", "L", "D"]),
    ("SH", "Shkëndija", 0, 0, 0, 0, 0, 0, 0, ["D", "L", "L", "W", "L"]),
    ("ZR", "Zrinjski", 0, 0, 0, 0, 0, 0, 0, ["L", "L", "D", "W", "W"]),
    ("SO", "Sigma Olomouc", 0, 0, 0, 0, 0, 0, 0, ["L", "W", "W", "L", "W"]),
    ("UC", "U. Craiova", 0, 0, 0, 0, 0, 0, 0, ["L", "W", "W", "L", "L"]),
    ("RI", "L. Red Imps", 0, 0, 0, 0, 0, 0, 0, ["W", "D", "L", "L", "W"]),
    ("DK", "Dynamo Kyiv", 0, 0, 0, 0, 0, 0, 0, ["L", "W", "L", "L", "W"]),
    ("LW", "Legia Warszawa", 0, 0, 0, 0, 0, 0, 0, ["D", "W", "L", "L", "L"]),
    ("SB", "S. Bratislava", 0, 0, 0, 0, 0, 0, 0, ["L", "D", "D", "W", "L"]),
    ("BR", "Breiðablik", 0, 0, 0, 0, 0, 0, 0, ["D", "W", "L", "D", "L"]),
    ("SR", "Shamrock Rovers", 0, 0, 0, 0, 0, 0, 0, ["L", "W", "W", "D", "W"]),
    ("HC", "Häcken", 0, 0, 0, 0, 0, 0, 0, ["L", "L", "W", "W", "L"]),
    ("HA", "Hamrun Spartans", 0, 0, 0, 0, 0, 0, 0, ["D", "L", "L", "L", "L"]),
    ("SB", "Shelbourne", 0, 0, 0, 0, 0, 0, 0, ["L", "D", "L", "L", "L"]),
    ("AB", "Aberdeen", 0, 0, 0, 0, 0, 0, 0, ["L", "L", "L", "L", "L"]),
    ("SK", "SK Rapid", 0, 0, 0, 0, 0, 0, 0, ["L", "L", "L", "L", "L"]),
]
