from sqlalchemy import update, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.data import ParseJob


async def sync_counters(
    db,
    site_name: str,
    success_count: int = 0,
    fail_count: int = 0,
):
    values = {}

    if success_count:
        values["processed_items"] = success_count

    if fail_count:
        values["error_items"] = fail_count

    # если дельты обе 0 — ничего не делаем
    if not values:
        return

    stmt = (
        update(ParseJob)
        .where(ParseJob.site_name == site_name)
        .values(**values)
    )

    await db.execute(stmt)


async def set_total_items(
    db,
    site_name: str,
    total: int,
):
    stmt = (
        update(ParseJob)
        .where(ParseJob.site_name == site_name)
        .values(total_items=total)
    )

    await db.execute(stmt)

async def get_all_jobs(db: AsyncSession):
    result = await db.execute(
        select(ParseJob).order_by(ParseJob.site_name)
    )
    return result.scalars().all()