from bs4 import BeautifulSoup


def extract_price(html: str) -> float | None:
    soup = BeautifulSoup(html, "lxml")

    # ---- 1. BEST SOURCE (SEO meta) ----
    meta = soup.select_one('meta[property="product:price:amount"]')
    if meta and meta.get("content"):
        try:
            return float(meta["content"])
        except ValueError:
            pass

    # ---- 2. JSON-LD fallback ----
    for script in soup.select('script[type="application/ld+json"]'):
        text = script.string or ""
        if '"price"' in text:
            import re
            m = re.search(r'"price"\s*:\s*"([\d.]+)"', text)
            if m:
                return float(m.group(1))

    return None