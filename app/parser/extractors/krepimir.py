from bs4 import BeautifulSoup
import re


def _extract_number(text: str) -> float | None:
    if not text:
        return None

    cleaned = text.replace("\xa0", "").replace(" ", "").strip()
    m = re.search(r"\d+(?:[.,]\d+)?", cleaned)
    if not m:
        return None

    return float(m.group(0).replace(",", "."))


def extract_price(html: str) -> float | None:
    low = html.lower()

    # --- 404 ---
    if "ошибка 404" in low or "страница не найдена" in low:
        return None

    soup = BeautifulSoup(html, "lxml")

    # ✅ главный контейнер товара
    product = soup.select_one(".middle_info.main_item_wrapper")
    if not product:
        return None

    # ✅ цена товара
    node = product.select_one(".price_value")
    if not node:
        return None

    return _extract_number("".join(node.stripped_strings))