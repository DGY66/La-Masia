from home_screen import HomeScreen
from ui import LeagueTableApp


def open_home() -> None:
    app = HomeScreen(open_table)
    app.mainloop()


def open_table(competition_key: str, season_key: str, language: str) -> None:
    app = LeagueTableApp(
        competition_key=competition_key,
        season_key=season_key,
        language=language,
        on_home=open_home,
    )
    app.mainloop()

if __name__ == "__main__":
    open_home()
