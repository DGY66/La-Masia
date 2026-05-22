from home_screen import HomeScreen
from ui import LeagueTableApp


def open_home() -> None:
    settings = _load_user_settings()
    app = HomeScreen(
        open_table,
        initial_league=settings.get("competition_key"),
        initial_season=settings.get("season_key"),
        initial_language=settings.get("language"),
    )
    app.mainloop()


def open_table(competition_key: str, season_key: str, language: str) -> None:
    _save_user_settings(competition_key, season_key, language)
    app = LeagueTableApp(
        competition_key=competition_key,
        season_key=season_key,
        language=language,
        on_home=open_home,
    )
    app.mainloop()


def _load_user_settings() -> dict[str, str]:
    try:
        from database import load_user_settings

        return load_user_settings()
    except Exception:
        return {}


def _save_user_settings(competition_key: str, season_key: str, language: str) -> None:
    try:
        from database import save_user_settings

        save_user_settings(competition_key, season_key, language)
    except Exception:
        return

if __name__ == "__main__":
    open_home()
