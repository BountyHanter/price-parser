from datetime import datetime, UTC
from typing import Any

from sqlalchemy import update

from app.models.data import ParseJob, ParseStatus


async def set_status(
    db,
    status: ParseStatus,
    site_name: str | None = None,
):
    now = datetime.now(UTC)
    values: dict[str, Any] = {
        "status": status,
    }

    # автоматические таймстемпы
    if status == ParseStatus.running:
        values["started_at"] = now

    if status in (ParseStatus.finished, ParseStatus.failed):
        values["finished_at"] = now

    stmt = update(ParseJob).values(**values)

    # если указан сайт — обновляем только его
    if site_name:
        stmt = stmt.where(ParseJob.site_name == site_name)

    await db.execute(stmt)

async def set_error(
    db,
    message: str,
    site_name: str | None = None,
):
    stmt = update(ParseJob).values(
        status=ParseStatus.failed,
        error_message=message,
        finished_at=datetime.now(UTC),
    )

    if site_name:
        stmt = stmt.where(ParseJob.site_name == site_name)

    await db.execute(stmt)