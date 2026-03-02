"""Mock data for when API is unavailable (rate limited)"""
from models import Team

def get_mock_teams() -> list[Team]:
    """Return mock UCL standings data (2024/25 season)"""
    mock_data = [
        ("LIV", "Liverpool", 8, 7, 0, 1, 17, 5, 21, ["L", "W", "W", "L", "W"]),
        ("BAR", "Barcelona", 8, 6, 1, 1, 28, 13, 19, ["L", "W", "D", "L", "W"]),
        ("ARS", "Arsenal", 8, 6, 1, 1, 16, 3, 19, ["W", "W", "W", "W", "W"]),
        ("INT", "Inter", 8, 6, 1, 1, 11, 1, 19, ["W", "W", "L", "L", "L"]),
        ("BAY", "Bayern München", 8, 6, 0, 2, 19, 8, 18, ["W", "W", "L", "W", "W"]),
        ("RMA", "Real Madrid", 8, 5, 2, 1, 18, 11, 17, ["W", "D", "W", "D", "W"]),
        ("MCI", "Manchester City", 8, 5, 1, 2, 15, 9, 16, ["W", "L", "W", "W", "L"]),
        ("PSG", "Paris Saint Germain", 8, 4, 3, 1, 12, 8, 15, ["D", "W", "D", "W", "D"]),
        ("JUV", "Juventus", 8, 4, 2, 2, 13, 7, 14, ["W", "W", "D", "L", "D"]),
        ("ATM", "Atletico Madrid", 8, 4, 2, 2, 15, 11, 14, ["L", "W", "D", "W", "W"]),
        ("ATA", "Atalanta", 8, 4, 2, 2, 14, 8, 14, ["W", "D", "W", "L", "D"]),
        ("LEV", "Bayer Leverkusen", 8, 4, 1, 3, 13, 10, 13, ["W", "W", "L", "L", "W"]),
        ("BVB", "Borussia Dortmund", 8, 4, 1, 3, 18, 11, 13, ["L", "W", "W", "W", "L"]),
        ("CHE", "Chelsea", 8, 4, 1, 3, 16, 13, 13, ["W", "L", "W", "W", "L"]),
        ("MIL", "AC Milan", 8, 4, 0, 4, 12, 12, 12, ["L", "W", "W", "L", "W"]),
        ("TOT", "Tottenham", 8, 3, 2, 3, 13, 11, 11, ["D", "W", "L", "W", "D"]),
        ("POR", "Porto", 8, 3, 2, 3, 11, 12, 11, ["L", "D", "W", "W", "D"]),
        ("LEI", "RB Leipzig", 8, 3, 1, 4, 9, 10, 10, ["L", "W", "L", "W", "W"]),
        ("NAP", "Napoli", 8, 3, 1, 4, 8, 12, 10, ["L", "L", "W", "W", "L"]),
        ("BEN", "Benfica", 8, 3, 0, 5, 10, 14, 9, ["W", "L", "L", "W", "L"]),
        ("SPO", "Sporting CP", 8, 2, 3, 3, 11, 12, 9, ["D", "L", "W", "D", "D"]),
        ("PSV", "PSV Eindhoven", 8, 2, 2, 4, 10, 13, 8, ["W", "L", "D", "L", "D"]),
        ("FEY", "Feyenoord", 8, 2, 2, 4, 9, 16, 8, ["L", "D", "W", "L", "D"]),
        ("MON", "Monaco", 8, 2, 1, 5, 8, 13, 7, ["L", "W", "L", "L", "W"]),
        ("FRA", "Eintracht Frankfurt", 8, 2, 1, 5, 10, 18, 7, ["L", "L", "W", "L", "W"]),
        ("BRU", "Club Brugge", 8, 2, 1, 5, 7, 15, 7, ["L", "W", "L", "L", "D"]),
        ("OLY", "Olympiacos", 8, 2, 0, 6, 6, 16, 6, ["L", "L", "W", "L", "W"]),
        ("GAL", "Galatasaray", 8, 1, 2, 5, 8, 17, 5, ["W", "D", "L", "L", "D"]),
        ("AJA", "Ajax", 8, 1, 1, 6, 7, 18, 4, ["L", "L", "W", "L", "L"]),
        ("MAR", "Marseille", 8, 1, 1, 6, 6, 19, 4, ["L", "L", "L", "W", "L"]),
        ("COP", "Copenhagen", 8, 1, 0, 7, 5, 20, 3, ["L", "L", "L", "W", "L"]),
        ("UNI", "Union SG", 8, 0, 2, 6, 4, 17, 2, ["D", "L", "L", "L", "D"]),
        ("SLA", "Slavia Praha", 8, 0, 1, 7, 3, 21, 1, ["L", "L", "L", "L", "D"]),
        ("ATH", "Athletic Club", 8, 0, 1, 7, 4, 22, 1, ["L", "L", "D", "L", "L"]),
        ("NEW", "Newcastle", 8, 0, 0, 8, 2, 23, 0, ["L", "L", "L", "L", "L"]),
        ("PAF", "Pafos", 8, 0, 0, 8, 1, 24, 0, ["L", "L", "L", "L", "L"]),
    ]

    teams = []
    for abbr, name, pld, w, d, l, gf, ga, pts, form in mock_data:
        team = Team(abbr, name)
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
