from __future__ import annotations

from typing import Final


LANGUAGES: Final[list[str]] = ["English", "Русский", "Кыргызча"]

SEASONS: Final[list[dict[str, str]]] = [
    {"key": "2526", "label": "2025 / 26", "tag_key": "current_season"},
    {"key": "2425", "label": "2024 / 25", "tag_key": "archive"},
    {"key": "2324", "label": "2023 / 24", "tag_key": "archive"},
    {"key": "2223", "label": "2022 / 23", "tag_key": "archive"},
    {"key": "2122", "label": "2021 / 22", "tag_key": "archive"},
    {"key": "2021", "label": "2020 / 21", "tag_key": "archive"},
    {"key": "1920", "label": "2019 / 20", "tag_key": "archive"},
    {"key": "1819", "label": "2018 / 19", "tag_key": "archive"},
    {"key": "1718", "label": "2017 / 18", "tag_key": "archive"},
    {"key": "1617", "label": "2016 / 17", "tag_key": "archive"},
    {"key": "1516", "label": "2015 / 16", "tag_key": "archive"},
]

HOME_TRANSLATIONS: Final[dict[str, dict[str, str]]] = {
    "English": {
        "title": "UEFA League Tables",
        "subtitle": "Select a season and a competition to view the standings",
        "app_title": "UEFA Competition Card",
        "choose_competition": "CHOOSE COMPETITION",
        "choose_subtitle": "Select your UEFA competition to get started",
        "select_season": "Select Season",
        "select": "Select",
        "season": "SEASON",
        "competition": "COMPETITION",
        "view_standings": "  View Standings  →",
        "current_season": "Current Season",
        "archive": "Archive",
        "competitions": {
            "ucl": "UEFA Champions League",
            "uel": "UEFA Europa League",
            "uecl": "UEFA Conference League",
        },
    },
    "Русский": {
        "title": "Таблицы лиг УЕФА",
        "subtitle": "Выберите сезон и турнир для просмотра таблиц",
        "app_title": "Карточка турниров УЕФА",
        "choose_competition": "ВЫБЕРИТЕ ТУРНИР",
        "choose_subtitle": "Выберите турнир УЕФА, чтобы начать",
        "select_season": "Выберите сезон",
        "select": "Выбрать",
        "season": "СЕЗОН",
        "competition": "ТУРНИР",
        "view_standings": "  Смотреть таблицы  →",
        "current_season": "Текущий сезон",
        "archive": "Архив",
        "competitions": {
            "ucl": "Лига чемпионов УЕФА",
            "uel": "Лига Европы УЕФА",
            "uecl": "Лига конференций УЕФА",
        },
    },
    "Кыргызча": {
        "title": "УЕФА лигаларынын таблицалары",
        "subtitle": "Таблицаларды көрүү үчүн сезонду жана турнирди тандаңыз",
        "app_title": "УЕФА турниринин картасы",
        "choose_competition": "ТУРНИРДИ ТАНДАҢЫЗ",
        "choose_subtitle": "Баштоо үчүн УЕФА турнирин тандаңыз",
        "select_season": "Сезон тандаңыз",
        "select": "Тандоо",
        "season": "СЕЗОН",
        "competition": "ТУРНИР",
        "view_standings": "  Таблицаларды көрүү  →",
        "current_season": "Учурдагы сезон",
        "archive": "Архив",
        "competitions": {
            "ucl": "УЕФА Чемпиондор Лигасы",
            "uel": "УЕФА Европа Лигасы",
            "uecl": "Конференция Лигасы",
        },
    },
}

TABLE_TRANSLATIONS: Final[dict[str, dict[str, object]]] = {
    "English": {
        "go_home": "Home",
        "final_stages": "Final stages",
        "back": "Back",
        "matches": "Matches",
        "by_date": "By date",
        "by_round": "By round",
        "final": "Final",
        "last_updated": "Last updated",
        "matchday": "Matchday {current} of {total}",
        "nav_to": "{name}",
        "mock_data": "League Phase {season} (Mock Data - API Unavailable)",
        "no_season_data_title": "No data for this season",
        "no_season_data_message": "UEFA Conference League started in 2021/22. Please return home.",
        "footer_design": "Design made by: Arsen, Eldiar\nPRG-28B",
        "footer_team": "La Masia Team",
        "columns": ["#", "CLUB", "PLD", "W", "D", "L", "For", "GA", "GD", "PTS", "FORM"],
        "sections": {
            "r16": "Straight to Round of 16",
            "seeded": "Knockout phase play-off places (Seeded)",
            "unseeded": "Knockout phase play-off places (Unseeded)",
            "elim": "Elimination places",
        },
        "qualified": "Qualified",
        "regulations": "Want to learn more about the format? Check the competition regulations",
        "disclaimer": (
            "Standings are provisional until all league phase matches have been played and officially validated by UEFA. "
            "Confirmations of qualification or elimination remain provisional until UEFA validates the final table."
        ),
        "competition_titles": {
            "ucl": "UEFA Champions League",
            "uel": "UEFA Europa League",
            "uecl": "UEFA Conference League",
        },
        "phase_labels": {
            "2526": "League Phase {season}",
            "2425": "League Phase {season}",
        },
    },
    "Русский": {
        "go_home": "Назад",
        "final_stages": "Финальные стадии",
        "back": "Назад",
        "matches": "Матчи",
        "by_date": "По дате",
        "by_round": "По раунду",
        "final": "Финал",
        "last_updated": "Обновлено",
        "matchday": "Тур {current} из {total}",
        "nav_to": "{name}",
        "mock_data": "Лиговый этап {season} (тестовые данные — API недоступен)",
        "no_season_data_title": "Нет данных за этот сезон",
        "no_season_data_message": "Лига конференций УЕФА началась в сезоне 2021/22. Вернитесь домой.",
        "footer_design": "Дизайн подготовили: Арсен, Элдиар\nPRG-28B",
        "footer_team": "Команда La Masia",
        "columns": ["#", "КЛУБ", "И", "В", "Н", "П", "ЗА", "ПР", "РМ", "ОЧКИ", "ФОРМА"],
        "sections": {
            "r16": "Прямой выход в 1/8 финала",
            "seeded": "Стыковые места плей-офф (сеяные)",
            "unseeded": "Стыковые места плей-офф (несеяные)",
            "elim": "Места вылета",
        },
        "qualified": "Квалификация",
        "regulations": "Подробнее о формате: регламент турнира",
        "disclaimer": (
            "Таблица носит предварительный характер, пока не сыграны и не подтверждены все матчи лигового этапа УЕФА. "
            "Статусы выхода и вылета считаются предварительными до утверждения итоговой таблицы."
        ),
        "competition_titles": {
            "ucl": "Лига чемпионов УЕФА",
            "uel": "Лига Европы УЕФА",
            "uecl": "Лига конференций УЕФА",
        },
        "phase_labels": {
            "2526": "Лиговый этап {season}",
            "2425": "Лиговый этап {season}",
        },
    },
    "Кыргызча": {
        "go_home": "Артка",
        "final_stages": "Финалдык баскычтар",
        "back": "Артка",
        "matches": "Оюндар",
        "by_date": "Дата боюнча",
        "by_round": "Раунд боюнча",
        "final": "Финал",
        "last_updated": "Жаңыртылган",
        "matchday": "{current}-тур / {total}",
        "nav_to": "{name}",
        "mock_data": "Лига этабы {season} (тесттик маалыматтар — API жеткиликсиз)",
        "no_season_data_title": "Бул сезон боюнча маалымат жок",
        "no_season_data_message": "УЕФА Конференция Лигасы 2021/22 сезонунда башталган. Үйгө кайтыңыз.",
        "footer_design": "Дизайн жасагандар: Арсен, Элдиар\nPRG-28B",
        "footer_team": "La Masia командасы",
        "columns": ["#", "КЛУБ", "ОЮН", "Ж", "Т", "У", "КИР", "ЧЫГ", "РМ", "УПАЙ", "ФОРМА"],
        "sections": {
            "r16": "Түз эле 1/8 финалга",
            "seeded": "Плей-офф орундары (себилген)",
            "unseeded": "Плей-офф орундары (себилбеген)",
            "elim": "Чыгып калуучу орундар",
        },
        "qualified": "Жолдомо алган",
        "regulations": "Формат тууралуу: турнирдин регламенти",
        "disclaimer": (
            "Бардык лига этабындагы оюндар бүткөнгө жана УЕФА тарабынан ырасталганга чейин таблица убактылуу болуп саналат. "
            "Чыгуу жана четтөө статустары да финалдык таблица бекитилгенге чейин убактылуу эсептелет."
        ),
        "competition_titles": {
            "ucl": "УЕФА Чемпиондор Лигасы",
            "uel": "УЕФА Европа Лигасы",
            "uecl": "УЕФА Конференция Лигасы",
        },
        "phase_labels": {
            "2526": "Лига этабы {season}",
            "2425": "Лига этабы {season}",
        },
    },
}


def get_home_strings(language: str) -> dict[str, str]:
    return HOME_TRANSLATIONS.get(language, HOME_TRANSLATIONS["English"])


def get_table_strings(language: str) -> dict[str, object]:
    return TABLE_TRANSLATIONS.get(language, TABLE_TRANSLATIONS["English"])


def get_competition_title(language: str, competition_key: str, fallback: str) -> str:
    strings = get_table_strings(language)
    titles = strings.get("competition_titles", {})
    if isinstance(titles, dict):
        value = titles.get(competition_key)
        if isinstance(value, str):
            return value
    return fallback
