import re

from bs4 import BeautifulSoup, Tag


def _read_labeled_price(section: Tag, price_class: str, label: str) -> float | None:
    for price in section.select(f".price-online .online-row > .{price_class}"):
        description = price.find_next_sibling("span")
        if description is None or " ".join(description.stripped_strings).casefold() != label:
            continue

        match = re.match(r"\s*(\d+(?:\s+\d{3})*(?:[.,]\d+)?)\s*₽", price.get_text())
        if match:
            return float("".join(match[1].split()).replace(",", "."))

    return None


def extract_prices(html: str) -> tuple[float | None, float | None]:
    """Return the retail and wholesale prices, in that order."""
    soup = BeautifulSoup(html, "lxml")

    section = soup.select_one("section.product-product-index-shop")
    if not section:
        return None, None

    retail = _read_labeled_price(section, "old-online", "розничная цена")
    wholesale = _read_labeled_price(section, "new-online", "оптовая цена")

    if retail is None:
        try:
            retail = float(section.get("data-price", ""))
        except ValueError:
            pass

    return retail, wholesale


def extract_price(html: str) -> float | None:
    retail, _ = extract_prices(html)
    return retail
