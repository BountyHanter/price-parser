import asyncio
import time

from app.fast_api_logger import log
from app.parser.config import AntiBlockConfig

class AntiBlockGuard:
    def __init__(self, site_name: str, cfg: AntiBlockConfig):
        self.site_name = site_name
        self.cfg = cfg

        self.forbidden_streak = 0
        self.cooldown_used = False
        self.post_cooldown_streak = 0

    async def handle_status(self, status: int) -> bool:
        """Возвращает True если воркер должен остановиться."""
        if status != 403:
            self.forbidden_streak = 0
            self.post_cooldown_streak = 0
            return False

        self.forbidden_streak += 1
        log.warning(f"[{self.site_name}] 403 streak = {self.forbidden_streak}")

        # --- первый порог ---
        if not self.cooldown_used and self.forbidden_streak >= self.cfg.max_403_streak:
            self.cooldown_used = True
            self.forbidden_streak = 0
            self.post_cooldown_streak = 0

            log.warning(f"[COOLDOWN] {self.site_name} sleep {self.cfg.cooldown_seconds}s")
            await asyncio.sleep(self.cfg.cooldown_seconds)
            return False

        # --- после cooldown ---
        if self.cooldown_used:
            self.post_cooldown_streak += 1
            log.warning(
                f"[{self.site_name}] post-cooldown 403 = "
                f"{self.post_cooldown_streak}/{self.cfg.post_cooldown_limit}"
            )

            if self.post_cooldown_streak >= self.cfg.post_cooldown_limit:
                log.error(f"[STOP] {self.site_name} blocked after cooldown")
                return True

        return False