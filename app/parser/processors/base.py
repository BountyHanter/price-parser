from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any
import httpx

from app.parser.schema import Task

class BaseProcessor(ABC):
    @abstractmethod
    async def process(
        self,
        client: httpx.AsyncClient,
        task: Task,
        memory: dict[str, Any],
    ) -> int:
        """Возвращает status-like код:
        - 200: обработано (даже если error=page_forbidden/price_not_found)
        - 403: считаем блоком (для анти-403 логики)
        - другие: по необходимости (например 400 bad url)
        """
        raise NotImplementedError