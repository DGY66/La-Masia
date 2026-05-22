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

HOME_TRANSLATIONS: Final[dict[str, dict[str, object]]] = {
    "English": {
        "app_title": "UEFA Competition Card",
        "choose_competition": "CHOOSE COMPETITION",
        "choose_subtitle": "Select your UEFA competition to get started",
        "select": "Select",
        "competitions": {
            "ucl": "UEFA Champions League",
            "uel": "UEFA Europa League",
            "uecl": "UEFA Conference League",
        },
        "title": "UEFA League Tables",
        "subtitle": "Select a season and a competition to view the standings",
        "season": "SEASON",
        "competition": "COMPETITION",
        "view_standings": "  View Standings  →",
        "current_season": "Current Season",
        "archive": "Archive",
    },
    "Русский": {
        "title": "Таблицы лиг УЕФА",
        "subtitle": "Выберите сезон и турнир для просмотра таблиц",
        "season": "СЕЗОН",
        "competition": "ТУРНИР",
        "view_standings": "  Смотреть таблицы  →",
        "current_season": "Текущий сезон",
        "archive": "Архив",
    },
    "Кыргызча": {
        "title": "УЕФА лигаларынын таблицалары",
        "subtitle": "Таблицаларды көрүү үчүн сезонду жана турнирди тандаңыз",
        "season": "СЕЗОН",
        "competition": "ТУРНИР",
        "view_standings": "  Таблицаларды көрүү  →",
        "current_season": "Учурдагы сезон",
        "archive": "Архив",
    },
}

TABLE_TRANSLATIONS: Final[dict[str, dict[str, object]]] = {
    "English": {
        "go_home": "Home",
        "knockout_stages": "Knockout stages",
        "knockout_stage_title": "{competition} Knockout stage",
        "back": "Back",
        "matches": "Matches",
        "by_date": "By date",
        "by_round": "By round",
        "final": "Final",
        "round_of_16": "Round of 16",
        "quarterfinals": "Quarterfinals",
        "semifinals": "Semifinals",
        "season": "Season",
        "no_knockout_data": "Knockout data is not available for this season.",
        "uecl_not_started": "UEFA Conference League started in the 2021/22 season. There is no data before that season.",
        "not_started": "Not played yet",
        "last_updated": "Last updated",
        "matchday": "Matchday {current} of {total}",
        "nav_to": "{name}",
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
        "knockout_stages": "Плей-офф",
        "knockout_stage_title": "{competition} Плей-офф",
        "back": "Назад",
        "matches": "Матчи",
        "by_date": "По дате",
        "by_round": "По раунду",
        "final": "Финал",
        "round_of_16": "1/8 финала",
        "quarterfinals": "Четвертьфиналы",
        "semifinals": "Полуфиналы",
        "season": "Сезон",
        "no_knockout_data": "Данные плей-офф для этого сезона недоступны.",
        "uecl_not_started": "Лига конференций УЕФА началась с сезона 2021/22. До этого сезона данных нет.",
        "not_started": "Еще не сыграно",
        "last_updated": "Обновлено",
        "matchday": "Тур {current} из {total}",
        "nav_to": "{name}",
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
        "knockout_stages": "Плей-офф",
        "knockout_stage_title": "{competition} Плей-офф",
        "back": "Артка",
        "matches": "Оюндар",
        "by_date": "Дата боюнча",
        "by_round": "Раунд боюнча",
        "final": "Финал",
        "round_of_16": "1/8 финал",
        "quarterfinals": "Чейрек финал",
        "semifinals": "Жарым финал",
        "season": "Сезон",
        "no_knockout_data": "Бул сезон үчүн плей-офф маалыматтары жок.",
        "uecl_not_started": "УЕФА Конференция Лигасы 2021/22 сезонунан башталган. Ага чейинки сезондор үчүн маалымат жок.",
        "not_started": "Азырынча ойноло элек",
        "last_updated": "Жаңыртылган",
        "matchday": "{current}-тур / {total}",
        "nav_to": "{name}",
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


def get_home_strings(language: str) -> dict[str, object]:
    strings = HOME_TRANSLATIONS["English"] | HOME_TRANSLATIONS.get(language, {})
    if language == LANGUAGES[1]:
        strings |= {
            "app_title": "Карточка турниров УЕФА",
            "choose_competition": "ВЫБЕРИТЕ ТУРНИР",
            "choose_subtitle": "Выберите турнир УЕФА, чтобы начать",
            "select_season": "Выберите сезон",
            "select": "Выбрать",
            "competitions": {
                "ucl": "Лига чемпионов УЕФА",
                "uel": "Лига Европы УЕФА",
                "uecl": "Лига конференций УЕФА",
            },
        }
    elif language == LANGUAGES[2]:
        strings |= {
            "app_title": "УЕФА турниринин картасы",
            "choose_competition": "ТУРНИРДИ ТАНДАҢЫЗ",
            "choose_subtitle": "Баштоо үчүн УЕФА турнирин тандаңыз",
            "select_season": "Сезон тандаңыз",
            "select": "Тандоо",
            "competitions": {
                "ucl": "УЕФА Чемпиондор Лигасы",
                "uel": "УЕФА Европа Лигасы",
                "uecl": "Конференция Лигасы",
            },
        }
    else:
        strings.setdefault("select_season", "Select Season")
    return strings


def get_table_strings(language: str) -> dict[str, object]:
    strings = TABLE_TRANSLATIONS["English"] | TABLE_TRANSLATIONS.get(language, {})
    if language == LANGUAGES[1]:
        strings["export_as"] = "Экспорт..."
    elif language == LANGUAGES[2]:
        strings["export_as"] = "Экспорт..."
    else:
        strings["export_as"] = "Export as..."
    return strings


def get_competition_title(language: str, competition_key: str, fallback: str) -> str:
    strings = get_table_strings(language)
    titles = strings.get("competition_titles", {})
    if isinstance(titles, dict):
        value = titles.get(competition_key)
        if isinstance(value, str):
            return value
    return fallback
