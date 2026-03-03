from bs4 import BeautifulSoup
import re


def _extract_number(text: str) -> float | None:
    if not text:
        return None

    match = re.search(r"\d+[.,]?\d*", text.replace(" ", ""))
    if not match:
        return None

    return float(match.group(0).replace(",", "."))


def _find_price_in_block(block):
    """
    Ищем первое число с ₽ внутри блока.
    """
    for el in block.find_all(string=True):
        if "₽" in el:
            price = _extract_number(el)
            if price is not None:
                return price
    return None


def extract_price(html: str) -> float | None:
    soup = BeautifulSoup(html, "lxml")

    # ищем ВСЕ блоки цены (не завязываемся на точные классы)
    price_blocks = soup.find_all(
        "div",
        class_=lambda c: c and "price" in c
    )

    regular_price = None

    for block in price_blocks:
        text = " ".join(block.stripped_strings).lower()
        if "при оплате онлайн" in text:
            online_price = _find_price_in_block(block)
            if online_price is not None:
                return online_price

        # ---- обычная цена (fallback) ----
        if regular_price is None:
            regular_price = _find_price_in_block(block)

    return regular_price