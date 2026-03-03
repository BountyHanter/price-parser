import asyncio
import random
import time
from typing import Any

import httpx

from app.database import new_session
from app.fast_api_logger import log
from app.models.data import ParseStatus
from app.parser.antiblock import AntiBlockGuard
from app.parser.config import ParserConfig, HEADERS
from app.parser.extractors.registry import REGISTRY
from app.parser.processors.html import HtmlProcessor
from app.parser.processors.sdvor import SdvorProcessor
from app.parser.config import SDVOR_CITIES, SDVOR_API_HEADERS
from app.utils.database.reset import reset_job
from app.utils.database.stats import set_total_items, sync_counters
from app.utils.database.status import set_status, set_error


def make_processor(site_name: str):
    if site_name == "СтройДвор":
        return SdvorProcessor(SDVOR_CITIES, SDVOR_API_HEADERS)

    extractor = REGISTRY.get(site_name)
    if extractor is None:
        raise RuntimeError(f"No extractor for site={site_name}")

    return HtmlProcessor(extractor)

async def site_worker(site_name: str, tasks, memory: dict[str, Any], cfg: ParserConfig):
    log.info(f"[START] {site_name} ({len(tasks)} задач)")
    async with new_session() as db:
        await reset_job(db, site_name)
        await set_status(db, ParseStatus.running, site_name)
        await set_total_items(db, site_name, len(tasks))
        await db.commit()


    success_count = 0
    fail_count = 0
    last_request_time = 0.0
    failed = False

    guard = AntiBlockGuard(site_name, cfg.antiblock)
    processor = make_processor(site_name)

    async with httpx.AsyncClient(
        headers=HEADERS,
        follow_redirects=True,
        timeout=cfg.http.request_timeout,
    ) as client:

        try:
            for task in tasks:
                # ---- delay between requests ----
                target_interval = random.uniform(cfg.delay.min_delay, cfg.delay.max_delay)

                now = time.monotonic()
                elapsed = now - last_request_time
                if elapsed < target_interval:
                    await asyncio.sleep(target_interval - elapsed)

                status = await processor.process(client, task, memory)

                # ---- 403 streak logic ----
                should_stop = await guard.handle_status(status)
                if should_stop:
                    failed = True
                    async with new_session() as db:
                        message_error = "Парсинг сайта остановился из за срабатывания защиты от ботов на сайте (403 продолжаются после ожидания)"
                        await set_error(db, site_name=site_name, message=message_error)
                        await db.commit()
                    break

                # ---- success/fail stats ----
                row = memory["rows"][str(task.row)]
                site_data = row["sites"][site_name]

                if status == 200 and site_data["error"] is None:
                    success_count += 1
                else:
                    fail_count += 1


                total = success_count + fail_count
                if total > 0 and total % 50 == 0:
                    log.info(f"[{site_name}] progress: ok={success_count} fail={fail_count}")

                if total > 0 and total % 10 == 0:
                    async with new_session() as db:
                        await sync_counters(
                            db,
                            site_name,
                            success_count=success_count,
                            fail_count=fail_count,
                        )
                        await db.commit()

                last_request_time = time.monotonic()
        except Exception as e:
            failed = True
            async with new_session() as db:
                await set_error(db, site_name=site_name, message=str(e) or type(e).__name__)
                await db.commit()
        finally:
            log.info(f"[DONE] {site_name}")
            async with new_session() as db:
                await sync_counters(db, site_name, success_count=success_count, fail_count=fail_count)
                if not failed:
                    await set_status(db, ParseStatus.finished, site_name)
                await db.commit()
