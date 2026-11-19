from dataclasses import dataclass

from openpyxl.worksheet.worksheet import Worksheet

CSK_SITE = "ЦСК"

SITES = {
    CSK_SITE: {"url_col": 6, "price_col": 14},
    "Крепеж 159": {"url_col": 7, "price_col": 15},
    "СтройДвор": {"url_col": 8, "price_col": 16},
    "УралМастер": {"url_col": 9, "price_col": 17},
    "ЭТМ": {"url_col": 10, "price_col": 18},
    "Креплайн": {"url_col": 11, "price_col": 19},
    "Креп": {"url_col": 12, "price_col": 20},
    "Крепимир": {"url_col": 13, "price_col": 21},
}


def resolve_price_columns(sheet: Worksheet) -> tuple[dict[str, int], int | None]:
    price_columns = {site: cols["price_col"] for site, cols in SITES.items()}
    retail_col = SITES[CSK_SITE]["price_col"]
    wholesale_col = retail_col + 1
    header = sheet.cell(row=2, column=wholesale_col).value
    normalized_header = " ".join(str(header or "").split()).casefold()
    if normalized_header != "цск опт1":
        return price_columns, None

    price_columns = {
        site: col + 1 if col >= wholesale_col else col
        for site, col in price_columns.items()
    }
    return price_columns, wholesale_col


@dataclass(frozen=True)
class Task:
    row: int
    site_name: str
    url_col: int
    price_col: int
    url: str
    price_cell: str
