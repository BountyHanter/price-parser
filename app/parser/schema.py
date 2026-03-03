from dataclasses import dataclass

SITES = {
    "ЦСК": {"url_col": 6, "price_col": 14},
    "Крепеж 159": {"url_col": 7, "price_col": 15},
    "СтройДвор": {"url_col": 8, "price_col": 16},
    "УралМастер": {"url_col": 9, "price_col": 17},
    "ЭТМ": {"url_col": 10, "price_col": 18},
    "Креплайн": {"url_col": 11, "price_col": 19},
    "Креп": {"url_col": 12, "price_col": 20},
    "Крепимир": {"url_col": 13, "price_col": 21},
}


@dataclass(frozen=True)
class Task:
    row: int
    site_name: str
    url_col: int
    price_col: int
    url: str
    price_cell: str
