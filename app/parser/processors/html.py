from typing import Any
import httpx

from app.fast_api_logger import log
from app.parser.schema import Task
from app.parser.processors.base import BaseProcessor

class HtmlProcessor(BaseProcessor):
    def __init__(self, extractor):
        self.extractor = extractor

    async def process(self, client: httpx.AsyncClient, task: Task, memory: dict[str, Any]) -> int:
        status = None
        price = None
        error = None

        try:
            response = await client.get(task.url)
            status = response.status_code
            html = response.text

            # ---- обработка 403 ----
            if status == 403:
                html_lower = html.lower()

                # ---- обычный forbidden (НЕ блокировка) ----
                if (
                    "you don't have permission" in html_lower
                    or "<h1>forbidden</h1>" in html_lower
                ):
                    error = "page_forbidden"
                    status = 200  # считаем успешной обработкой
                else:
                    # потенциальный блок
                    return 403

            elif status != 200:
                raise RuntimeError(f"HTTP {status}")

            # ---- извлекаем цену только при нормальном ответе ----
            if error is None:
                price = self.extractor.extract_price(html)
                if price is None:
                    error = "price_not_found"

        except Exception as e:
            price = None
            error = str(e) or type(e).__name__

        # запись в memory
        row_data = memory["rows"][str(task.row)]
        site_data = row_data["sites"][task.site_name]
        site_data["price"] = price
        site_data["error"] = error

        if error is not None:
            log.info(
                f"[{task.site_name}] "
                f"row={task.row} "
                f"price_cell={task.price_cell} "
                f"price={price} "
                f"error={error}"
            )

        return int(status or 0)