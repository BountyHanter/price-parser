from urllib.parse import urlparse

def parse_sdvor_url(url: str):
    try:
        parsed = urlparse(url)
        parts = parsed.path.strip("/").split("/")
        if len(parts) < 3:
            return None

        city = parts[0]
        slug = parts[-1].split("#")[0]
        code = slug.split("-")[-1]

        if not code.isdigit():
            return None

        return city, code

    except Exception:
        return None