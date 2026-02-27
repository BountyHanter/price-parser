from collections import defaultdict
from urllib.parse import urlparse

import httpx

from app.parser.create_tasks import read_tasks_from_excel
from app.parser.schema import Task

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": (
        "text/html,application/xhtml+xml,application/xml;q=0.9,"
        "image/avif,image/webp,*/*;q=0.8"
    ),
    "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
}


# ---------- grouping ----------

def group_tasks_by_domain(tasks: list[Task]):
    grouped: dict[str, list[Task]] = defaultdict(list)

    for t in tasks:
        domain = urlparse(t.url).netloc
        grouped[domain].append(t)

    return grouped


# ---------- calibration ----------

async def calibrate_domain(domain: str, tasks: list[Task], sample_size: int = 10):
    delay = 2.0
    sample = tasks[:sample_size]

    print(f"\n=== CALIBRATING {domain} ===")

    async with httpx.AsyncClient(
        headers=HEADERS,
        follow_redirects=True,
    ) as client:

        for task in sample:

            while True:
                try:
                    r = await client.get(task.url, timeout=25)
                    code = r.status_code
                except Exception as e:
                    print(f"{domain} ERROR: {e}")
                    code = 0

                print(
                    f"{domain} | row={task.row} | "
                    f"status={code} | delay={delay:.1f}s"
                )

                if code == 200:
                    await asyncio.sleep(delay)
                    break

                if code == 403:
                    delay += 1
                    print(f"{domain} ↑ delay increased → {delay:.1f}s")
                    print(f"{domain} cooldown 40s...\n")

                    await asyncio.sleep(40)

    print(f"=== DONE {domain} → final delay {delay:.1f}s ===")
    return domain, delay


# ---------- main ----------

async def calibrate_domains(tasks: list[Task]):
    grouped = group_tasks_by_domain(tasks)

    results: dict[str, float] = {}

    # калибруем ПОСЛЕДОВАТЕЛЬНО (безопасно)
    for domain, domain_tasks in grouped.items():
        domain, delay = await calibrate_domain(domain, domain_tasks, 50)
        results[domain] = delay

    print("\n========== FINAL DELAYS ==========")
    for domain, delay in results.items():
        print(f"{domain:30} -> {delay:.1f}s")

    return results

if __name__ == "__main__":
    import asyncio

    tasks = read_tasks_from_excel("template.xlsx")

    asyncio.run(calibrate_domains(tasks))