from sqlalchemy import update

from app.models.data import ParseJob


async def reset_job(db, site_name: str):
    stmt = (
        update(ParseJob)
        .where(ParseJob.site_name == site_name)
        .values(
            processed_items=0,
            error_items=0,
            total_items=0,
            started_at=None,
            finished_at=None,
            error_message=None,
        )
    )
    await db.execute(stmt)