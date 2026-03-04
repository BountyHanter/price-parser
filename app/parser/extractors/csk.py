from bs4 import BeautifulSoup


def extract_price(html: str) -> float | None:
    soup = BeautifulSoup(html, "lxml")

    section = soup.select_one("section.product-product-index-shop")
    if not section:
        return None

    price = section.get("data-price")
    if not price:
        return None

    try:
        return float(price)
    except ValueError:
        return None