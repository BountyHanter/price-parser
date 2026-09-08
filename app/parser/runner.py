import asyncio
import faulthandler
import json
import signal
import sys
from collections import defaultdict
from typing import Any

from app.database import new_session
from app.fast_api_logger import log
from app.models.data import ParseStatus
from app.parser.config import ParserConfig
from app.parser.create_tasks import read_tasks_from_excel
from app.parser.insert_data import write_prices
from app.parser.memory_form import build_memory_structure
from app.parser.paths import JSON_PATH, XLSX_PATH
from app.parser.worker import site_worker
from app.utils.database.status import set_status, set_error


def _termination_handler(signum, _frame):
    """Сохраняет причину штатного завершения от systemd в stderr парсера."""
    signal_name = signal.Signals(signum).name
    print(
        f"[FATAL] Parser received {signal_name} ({signum}); process is terminating",
        file=sys.stderr,
        flush=True,
    )
    raise SystemExit(128 + signum)


def group_tasks_by_site(tasks):
    grouped = defaultdict(list)
    for t in tasks:
        grouped[t.site_name].append(t)
    return grouped

async def main():
    try:
        cfg = ParserConfig()

        # читаем задачи
        tasks = read_tasks_from_excel(XLSX_PATH)
        if cfg.task_limit:
            tasks = tasks[:cfg.task_limit]

        # создаём memory
        memory: dict[str, Any] = build_memory_structure(XLSX_PATH, tasks)

        # группируем по сайтам
        grouped = group_tasks_by_site(tasks)

        workers = [
            asyncio.create_task(site_worker(site_name, site_tasks, memory, cfg))
            for site_name, site_tasks in grouped.items()
        ]
        results = await asyncio.gather(*workers, return_exceptions=True)

        for r in results:
            if isinstance(r, Exception):
                log.exception("Worker crashed", exc_info=r)

        JSON_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(JSON_PATH, "w", encoding="utf-8") as f:
            json.dump(memory, f, ensure_ascii=False, indent=2)

        log.info("result.json сохранён")

        try:
            write_prices()
            async with new_session() as db:
                await set_status(db, ParseStatus.created)
                await db.commit()

        except Exception as e:
            error_message = f"Ошибка при сохранении Excel - {e}"
            async with new_session() as db:
                await set_error(db, error_message)
                await db.commit()

    except BaseException as e:
        # BaseException покрывает SystemExit, возникающий при SIGTERM.
        # Обычный except Exception такой случай не логировал.
        log.exception(f"runner fatal exception - {e or type(e).__name__}")
        raise




if __name__ == "__main__":
    # Выводит traceback при фатальных ошибках интерпретатора (например, segfault)
    # в stderr, который main.py направляет в storage/parser_process.log.
    faulthandler.enable(file=sys.stderr, all_threads=True)
    signal.signal(signal.SIGTERM, _termination_handler)
    signal.signal(signal.SIGINT, _termination_handler)
    asyncio.run(main())
