from __future__ import annotations

from typing import Final


LANG_EN: Final[str] = "English"
LANG_RU: Final[str] = "Русский"
LANG_KY: Final[str] = "Кыргызча"

LANGUAGES: Final[list[str]] = [LANG_KY, LANG_RU, LANG_EN]

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

COMPETITION_TITLES: Final[dict[str, dict[str, str]]] = {
    LANG_EN: {
        "ucl": "UEFA Champions League",
        "uel": "UEFA Europa League",
        "uecl": "UEFA Conference League",
    },
    LANG_RU: {
        "ucl": "Лига чемпионов УЕФА",
        "uel": "Лига Европы УЕФА",
        "uecl": "Лига конференций УЕФА",
    },
    LANG_KY: {
        "ucl": "УЕФА Чемпиондор Лигасы",
        "uel": "УЕФА Европа Лигасы",
        "uecl": "УЕФА Конференция Лигасы",
    },
}

HOME_TRANSLATIONS: Final[dict[str, dict[str, object]]] = {
    LANG_EN: {
        "app_title": "UEFA Competition Card",
        "choose_competition": "CHOOSE COMPETITION",
        "choose_subtitle": "Select your UEFA competition to get started",
        "select_season": "Select season",
        "select": "Select",
        "competitions": COMPETITION_TITLES[LANG_EN],
        "title": "UEFA League Tables",
        "subtitle": "Select a season and a competition to view the standings",
        "season": "SEASON",
        "competition": "COMPETITION",
        "view_standings": "View standings",
        "current_season": "Current season",
        "archive": "Archive",
    },
    LANG_RU: {
        "app_title": "Турниры УЕФА",
        "choose_competition": "ВЫБЕРИТЕ ТУРНИР",
        "choose_subtitle": "Выберите сезон и турнир УЕФА",
        "select_season": "Выберите сезон",
        "select": "Выбрать",
        "competitions": COMPETITION_TITLES[LANG_RU],
        "title": "Таблицы лиг УЕФА",
        "subtitle": "Выберите сезон и турнир для просмотра таблицы",
        "season": "СЕЗОН",
        "competition": "ТУРНИР",
        "view_standings": "Смотреть таблицу",
        "current_season": "Текущий сезон",
        "archive": "Архив",
    },
    LANG_KY: {
        "app_title": "УЕФА турнирлери",
        "choose_competition": "ТУРНИРДИ ТАНДАҢЫЗ",
        "choose_subtitle": "Сезонду жана УЕФА турнирин тандаңыз",
        "select_season": "Сезонду тандаңыз",
        "select": "Тандоо",
        "competitions": COMPETITION_TITLES[LANG_KY],
        "title": "УЕФА лигаларынын таблицалары",
        "subtitle": "Таблицаны көрүү үчүн сезонду жана турнирди тандаңыз",
        "season": "СЕЗОН",
        "competition": "ТУРНИР",
        "view_standings": "Таблицаны көрүү",
        "current_season": "Учурдагы сезон",
        "archive": "Архив",
    },
}

TABLE_TRANSLATIONS: Final[dict[str, dict[str, object]]] = {
    LANG_EN: {
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
        "play_off": "Play-off",
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
        "competition_titles": COMPETITION_TITLES[LANG_EN],
        "phase_labels": {
            "default": "League Phase {season}",
            "2324": "Group Stage {season}",
            "2223": "Group Stage {season}",
            "2122": "Group Stage {season}",
            "2021": "Group Stage {season}",
            "1920": "Group Stage {season}",
            "1819": "Group Stage {season}",
            "1718": "Group Stage {season}",
            "1617": "Group Stage {season}",
            "1516": "Group Stage {season}",
        },
        "mock_phase_label": "League Phase {season} (Mock data - API unavailable)",
        "export_as": "Export as...",
        "export": "Export",
        "export_failed": "Export failed",
        "export_complete": "Export complete",
        "saved": "Saved:\n{path}",
        "filetypes": {
            "all": "All files",
            "csv": "CSV files",
            "txt": "Text files",
            "json": "JSON files",
            "excel": "Excel files",
        },
        "export_headers": ["round", "date", "home", "home_score", "away", "away_score", "note"],
    },
    LANG_RU: {
        "go_home": "Главная",
        "knockout_stages": "Плей-офф",
        "knockout_stage_title": "{competition}: плей-офф",
        "back": "Назад",
        "matches": "Матчи",
        "by_date": "По дате",
        "by_round": "По раунду",
        "final": "Финал",
        "round_of_16": "1/8 финала",
        "quarterfinals": "Четвертьфинал",
        "semifinals": "Полуфинал",
        "play_off": "Плей-офф",
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
            "seeded": "Места в стыковых матчах плей-офф (сеяные)",
            "unseeded": "Места в стыковых матчах плей-офф (несеяные)",
            "elim": "Места вылета",
        },
        "qualified": "Квалифицировались",
        "regulations": "Подробнее о формате: регламент турнира",
        "disclaimer": (
            "Таблица предварительная, пока все матчи лигового этапа не сыграны и не подтверждены УЕФА. "
            "Статусы выхода и вылета считаются предварительными до утверждения итоговой таблицы."
        ),
        "competition_titles": COMPETITION_TITLES[LANG_RU],
        "phase_labels": {
            "default": "Лиговый этап {season}",
            "2324": "Групповой этап {season}",
            "2223": "Групповой этап {season}",
            "2122": "Групповой этап {season}",
            "2021": "Групповой этап {season}",
            "1920": "Групповой этап {season}",
            "1819": "Групповой этап {season}",
            "1718": "Групповой этап {season}",
            "1617": "Групповой этап {season}",
            "1516": "Групповой этап {season}",
        },
        "mock_phase_label": "Лиговый этап {season} (тестовые данные - API недоступен)",
        "export_as": "Экспорт...",
        "export": "Экспорт",
        "export_failed": "Ошибка экспорта",
        "export_complete": "Экспорт завершен",
        "saved": "Сохранено:\n{path}",
        "filetypes": {
            "all": "Все файлы",
            "csv": "CSV-файлы",
            "txt": "Текстовые файлы",
            "json": "JSON-файлы",
            "excel": "Excel-файлы",
        },
        "export_headers": ["раунд", "дата", "хозяева", "счет_хозяев", "гости", "счет_гостей", "примечание"],
    },
    LANG_KY: {
        "go_home": "Башкы бет",
        "knockout_stages": "Плей-офф",
        "knockout_stage_title": "{competition}: плей-офф",
        "back": "Артка",
        "matches": "Оюндар",
        "by_date": "Дата боюнча",
        "by_round": "Раунд боюнча",
        "final": "Финал",
        "round_of_16": "1/8 финал",
        "quarterfinals": "Чейрек финал",
        "semifinals": "Жарым финал",
        "play_off": "Плей-офф",
        "season": "Сезон",
        "no_knockout_data": "Бул сезон үчүн плей-офф маалыматы жок.",
        "uecl_not_started": "УЕФА Конференция Лигасы 2021/22 сезонунан башталган. Ага чейинки сезондор үчүн маалымат жок.",
        "not_started": "Азырынча ойноло элек",
        "last_updated": "Жаңыртылган",
        "matchday": "{current}-тур / {total}",
        "nav_to": "{name}",
        "columns": ["#", "КЛУБ", "ОЮН", "Ж", "Т", "У", "КИР", "ЧЫГ", "РМ", "УПАЙ", "ФОРМА"],
        "sections": {
            "r16": "Түз 1/8 финалга чыгуу",
            "seeded": "Плей-офф стык орундары (себилген)",
            "unseeded": "Плей-офф стык орундары (себилбеген)",
            "elim": "Чыгып калуучу орундар",
        },
        "qualified": "Жолдомо алды",
        "regulations": "Формат тууралуу: турнирдин регламенти",
        "disclaimer": (
            "Лига этабындагы бардык оюндар бүтүп, УЕФА тарабынан расмий ырасталмайынча таблица убактылуу болуп саналат. "
            "Чыгуу жана четтетүү статустары да акыркы таблица бекитилгенге чейин убактылуу."
        ),
        "competition_titles": COMPETITION_TITLES[LANG_KY],
        "phase_labels": {
            "default": "Лига этабы {season}",
            "2324": "Топтук этап {season}",
            "2223": "Топтук этап {season}",
            "2122": "Топтук этап {season}",
            "2021": "Топтук этап {season}",
            "1920": "Топтук этап {season}",
            "1819": "Топтук этап {season}",
            "1718": "Топтук этап {season}",
            "1617": "Топтук этап {season}",
            "1516": "Топтук этап {season}",
        },
        "mock_phase_label": "Лига этабы {season} (тесттик маалымат - API жеткиликсиз)",
        "export_as": "Экспорт...",
        "export": "Экспорт",
        "export_failed": "Экспорт катасы",
        "export_complete": "Экспорт бүттү",
        "saved": "Сакталды:\n{path}",
        "filetypes": {
            "all": "Бардык файлдар",
            "csv": "CSV файлдары",
            "txt": "Текст файлдары",
            "json": "JSON файлдары",
            "excel": "Excel файлдары",
        },
        "export_headers": ["раунд", "дата", "үй ээси", "үй_эсеби", "конок", "конок_эсеби", "эскертүү"],
    },
}


def _merge(base: dict[str, object], override: dict[str, object]) -> dict[str, object]:
    merged = dict(base)
    merged.update(override)
    return merged


def get_home_strings(language: str) -> dict[str, object]:
    return _merge(HOME_TRANSLATIONS[LANG_EN], HOME_TRANSLATIONS.get(language, {}))


def get_table_strings(language: str) -> dict[str, object]:
    return _merge(TABLE_TRANSLATIONS[LANG_EN], TABLE_TRANSLATIONS.get(language, {}))


def get_competition_title(language: str, competition_key: str, fallback: str) -> str:
    strings = get_table_strings(language)
    titles = strings.get("competition_titles", {})
    if isinstance(titles, dict):
        value = titles.get(competition_key)
        if isinstance(value, str):
            return value
    return fallback
