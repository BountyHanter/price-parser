from bs4 import BeautifulSoup
import re


def _extract_number(text: str) -> float | None:
    if not text:
        return None

    cleaned = text.replace("\xa0", " ").strip()
    m = re.search(r"\d+(?:[.,]\d+)?", cleaned.replace(" ", ""))
    if not m:
        return None

    return float(m.group(0).replace(",", "."))


def extract_price(html: str) -> float | None:
    soup = BeautifulSoup(html, "lxml")

    for param in soup.select(".item__productParam"):
        name = param.select_one(".item__productParam-name")
        if not name:
            continue

        name_text = name.get_text().replace("\n", " ").strip().lower()

        if "цена при заказе через сайт" in name_text:
            val = param.select_one(".item__productParam-val")
            if not val:
                return None

            text = val.get_text().replace("\n", " ").strip()
            return _extract_number(text)

    return None