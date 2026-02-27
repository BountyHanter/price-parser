import asyncio
import random
from collections import defaultdict
from urllib.parse import urlparse
import httpx

from app.parser.browser import sdvor_browser_worker
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


def group_tasks_by_domain(tasks: list[Task]):
    grouped: dict[str, list[Task]] = defaultdict(list)

    for t in tasks:
        domain = urlparse(t.url).netloc
        grouped[domain].append(t)

    return grouped


async def fetch_status(task: Task, client: httpx.AsyncClient):
    try:
        r = await client.get(task.url, timeout=20)

        print(
            f"[{task.site_name}] "
            f"{urlparse(task.url).netloc} "
            f"row={task.row} -> {r.status_code}"
        )

    except Exception as e:
        print(
            f"[{task.site_name}] "
            f"{urlparse(task.url).netloc} "
            f"row={task.row} ERROR: {e}"
        )


async def domain_worker(domain: str, domain_tasks: list[Task]):
    print(f"START worker: {domain} ({len(domain_tasks)} tasks)")

    async with httpx.AsyncClient(
        headers=HEADERS,
        follow_redirects=True,
    ) as client:

        for task in domain_tasks:
            await fetch_status(task, client)

            sleep_time = random.uniform(1.5, 3.5)

            await asyncio.sleep(sleep_time)

    print(f"END worker: {domain}")


async def run_test(tasks: list[Task]):
    grouped = group_tasks_by_domain(tasks)

    workers = []

    for domain, domain_tasks in grouped.items():

        # ---- SDVOR → браузер ----
        if "sdvor.com" in domain:
            print(f"USE BROWSER WORKER: {domain}")
            workers.append(sdvor_browser_worker(domain_tasks))

        # ---- остальные сайты → httpx ----
        else:
            workers.append(domain_worker(domain, domain_tasks))

    await asyncio.gather(*workers)
if __name__ == "__main__":
    from app.parser.create_tasks import read_tasks_from_excel
    import asyncio

    tasks = read_tasks_from_excel("template.xlsx")

    asyncio.run(run_test(tasks[:40]))  # сначала маленький тест