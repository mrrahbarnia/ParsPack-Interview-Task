from typing import Sequence

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession

from .db_models import Job as DBJob
from ..types import JobID, JobStatus, JobResult
from ..domain.models import Job as DomainJob

from src.shared.const import DBLock


class JobRepo:
    def __init__(self) -> None:
        pass

    async def get_id_by_text(self, session: AsyncSession, text: str) -> JobID | None:
        stmt = sa.select(DBJob.id).where(DBJob.text == text).limit(1)
        job_id = await session.scalar(stmt)
        return job_id

    async def add(self, session: AsyncSession, text: str) -> JobID | None:
        stmt = sa.insert(DBJob).values({DBJob.text: text}).returning(DBJob.id)
        job_id = await session.scalar(stmt)
        return job_id

    async def get_pending_jobs(
        self, session: AsyncSession, lock: DBLock, limit: int = 1
    ) -> Sequence[DomainJob]:
        stmt = sa.select(DBJob).where(DBJob.status == JobStatus.PENDING).limit(limit)

        if lock.is_active:
            await session.execute(
                sa.text(f"SET LOCAL lock_timeout = '{lock.timeout_second}s'")
            )
            stmt = stmt.with_for_update(skip_locked=lock.skip_locked)

        jobs = (await session.scalars(stmt)).all()

        domain_jobs: list[DomainJob] = []
        for job in jobs:
            domain_jobs.append(DomainJob(id=job.id, text=job.text))

        return domain_jobs

    async def mark_job_as_completed(
        self, session: AsyncSession, id: JobID, result: JobResult
    ) -> None:
        stmt = (
            sa.update(DBJob)
            .values({DBJob.status: JobStatus.COMPLETED, DBJob.result: result})
            .where(DBJob.id == id)
        )

        await session.execute(stmt)

    async def mark_job_as_failed(
        self, session: AsyncSession, id: JobID, processing_error: str | None = None
    ) -> None:
        stmt = (
            sa.update(DBJob)
            .values(
                {
                    DBJob.status: JobStatus.FAILED,
                    DBJob.processing_error: processing_error,
                }
            )
            .where(DBJob.id == id)
        )

        await session.execute(stmt)
