import asyncio
import random

from playwright.async_api import async_playwright

from app.parser.schema import Task


async def human_behavior(page):
    """Небольшая имитация пользователя (~1 сек движения мыши)"""

    for _ in range(5):
        await page.mouse.move(
            random.randint(200, 900),
            random.randint(200, 700),
            steps=20,
        )
        await asyncio.sleep(0.2)


async def sdvor_browser_worker(tasks: list[Task]):
    print(f"START browser worker sdvor ({len(tasks)} tasks)")

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False  # можно True позже
        )

        context = await browser.new_context(
            locale="ru-RU",
            viewport={"width": 1280, "height": 900},
        )

        page = await context.new_page()

        for task in tasks:
            try:
                print(f"[SDVOR] open row={task.row}")

                # быстрый переход — НЕ ждём загрузку
                await page.goto(task.url, wait_until="commit")

                # страница появилась
                await asyncio.sleep(1)

                # движение мышью ~1 сек
                await human_behavior(page)

                print(f"[SDVOR] visited row={task.row}")

                # имитация чтения страницы
                await asyncio.sleep(2)

            except Exception as e:
                print(f"[SDVOR] ERROR row={task.row}: {e}")

        await browser.close()

    print("END browser worker sdvor")