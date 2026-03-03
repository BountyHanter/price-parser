from sqlalchemy import select

from app.database import engine, Base, new_session
from app.models.data import ParseJob
from app.parser.schema import SITES


async def seed_parser_sites(session):
    result = await session.execute(select(ParseJob.site_name))
    existing_names = set(result.scalars().all())

    for site_name in SITES.keys():
        if site_name not in existing_names:
            session.add(
                ParseJob(
                    site_name=site_name,
                )
            )

    await session.commit()

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with new_session() as session:
        await seed_parser_sites(session)