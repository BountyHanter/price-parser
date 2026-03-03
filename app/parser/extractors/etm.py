from bs4 import BeautifulSoup
import re


def _extract_number(text: str) -> float | None:
    if not text:
        return None

    cleaned = text.replace("\xa0", " ").strip()
    m = re.search(r"\d[\d\s]*[.,]\d+|\d[\d\s]*", cleaned)
    if not m:
        return None

    return float(m.group(0).replace(" ", "").replace(",", "."))


def extract_price(html: str) -> float | None:
    soup = BeautifulSoup(html, "lxml")

    # ---- товар не поставляется ----
    if soup.find(string=re.compile(r"Товар\s+не\s+поставляется", re.I)):
        return None

    # =====================================================
    # 1️⃣ ГЛАВНАЯ цена товара (самая надёжная)
    # =====================================================
    main_price = soup.select_one('[class*="priceMain"]')
    if main_price:
        price = _extract_number("".join(main_price.stripped_strings))
        if price:
            return price

    # =====================================================
    # 2️⃣ price-details (аккордеон)
    # =====================================================
    nodes = soup.select('[data-testid^="catalog-list-item-price-details-"]')

    for node in nodes:
        if "-unit" in node.get("data-testid", ""):
            continue

        price = _extract_number("".join(node.stripped_strings))
        if price:
            return price

    # =====================================================
    # 3️⃣ fallback price560
    # =====================================================
    nodes = soup.select('[data-testid^="catalog-list-item-price560-"]')

    for node in nodes:
        if "-unit" in node.get("data-testid", ""):
            continue

        price = _extract_number("".join(node.stripped_strings))
        if price:
            return price

    return None