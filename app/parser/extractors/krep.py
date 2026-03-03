from bs4 import BeautifulSoup
import re


def _extract_number(text: str) -> float | None:
    if not text:
        return None

    cleaned = text.replace("\xa0", " ").strip()

    m = re.search(r"\d[\d\s]*[.,]\d+|\d+", cleaned)
    if not m:
        return None

    return float(m.group(0).replace(" ", "").replace(",", "."))


def extract_price(html: str) -> float | None:
    # --- быстрые проверки ошибок страницы ---
    low = html.lower()

    if "товар не найден!" in html:
        return None

    if "<h1>forbidden</h1>" in low or "you don't have permission" in low:
        return None

    soup = BeautifulSoup(html, "lxml")

    # ✅ главный контейнер товара (важно!)
    product = soup.select_one(".us-product-info")
    if not product:
        return None

    # 1️⃣ цена со скидкой (если есть)
    node = product.select_one(".us-price-new")
    if node:
        price = _extract_number("".join(node.stripped_strings))
        if price is not None:
            return price

    # 2️⃣ обычная цена
    node = product.select_one(".us-price-actual")
    if node:
        price = _extract_number("".join(node.stripped_strings))
        if price is not None:
            return price

    return None