from typing import Any, Sequence
import asyncio
import httpx

from app.fast_api_logger import log
from app.parser.schema import Task
from app.parser.processors.base import BaseProcessor
from app.parser.processors.utils import parse_sdvor_url

class SdvorProcessor(BaseProcessor):
    def __init__(self, cities: Sequence[str], api_headers: dict[str, str]):
        self.cities = list(cities)
        self.api_headers = api_headers

    async def process(self, client: httpx.AsyncClient, task: Task, memory: dict[str, Any]) -> int:
        status = None
        parsed = parse_sdvor_url(task.url)

        if not parsed:
            error = "bad_sdvor_url"
            price = None
            status = 400
        else:
            original_city, code = parsed
            cities_to_try = [original_city] + [c for c in self.cities if c != original_city]

            price = None
            error = None

            for city in cities_to_try:
                api_url = f"https://api-gateway.sdvor.com/occ/v2/sd/products/{code}"
                params = {
                    "fields": "FULL",
                    "curr": "RUB",
                    "lang": "ru",
                    "baseStore": city,
                }

                try:
                    r = await client.get(api_url, params=params, headers=self.api_headers)
                    status = r.status_code
                    if status != 200:
                        continue

                    data = r.json()

                    # ✅ SAP ошибка внутри JSON
                    if "errors" in data:
                        await asyncio.sleep(2)
                        msg = data["errors"][0].get("message", "")

                        # именно ошибка города → пробуем следующий
                        if "Base store" in msg:
                            continue

                        # другая API ошибка — фиксируем
                        error = msg
                        break

                    # ✅ нормальный ответ
                    price_val = data.get("price", {}).get("value")
                    if price_val is not None:
                        price = float(price_val)
                        error = None
                        break

                except Exception as e:
                    error = str(e) or type(e).__name__

            if price is None and error is None:
                error = "no_valid_city"

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