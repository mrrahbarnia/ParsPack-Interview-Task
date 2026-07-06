import sqlalchemy as sa

from sqlalchemy.ext.asyncio import AsyncSession

from .db_models import Job
from ..types import JobID


class JobRepo:
    def __init__(self) -> None:
        pass

    async def get_id_by_text(self, session: AsyncSession, text: str) -> JobID | None:
        stmt = sa.select(Job.id).where(Job.text == text).limit(1)
        job_id = await session.scalar(stmt)
        return job_id

    async def add(self, session: AsyncSession, text: str) -> JobID | None:
        stmt = sa.insert(Job).values({Job.text: text}).returning(Job.id)
        job_id = await session.scalar(stmt)
        return job_id
