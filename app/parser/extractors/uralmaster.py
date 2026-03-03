from bs4 import BeautifulSoup
import re


def _extract_number(text: str) -> float | None:
    if not text:
        return None

    m = re.search(r"\d+(?:[.,]\d+)?", text.replace("\xa0", "").replace(" ", ""))
    if not m:
        return None

    return float(m.group(0).replace(",", "."))


def extract_price(html: str) -> float | None:
    soup = BeautifulSoup(html, "lxml")

    node = soup.select_one(".item_current_price")
    if not node:
        return None

    text = "".join(node.stripped_strings)
    return _extract_number(text)