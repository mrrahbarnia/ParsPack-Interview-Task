from typing import Protocol, Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from ..types import JobID, JobResult
from ..domain.models import Job as DomainJob

from src.shared.const import DBLock


class IJobRepo(Protocol):
    async def get_id_by_text(
        self, session: AsyncSession, text: str
    ) -> JobID | None: ...
    async def get_by_id(
        self, session: AsyncSession, id: JobID, lock: DBLock
    ) -> DomainJob | None: ...
    async def add(self, session: AsyncSession, text: str) -> JobID | None: ...
    async def get_pending_job_ids(
        self, session: AsyncSession, lock: DBLock, limit: int = 1
    ) -> Sequence[JobID]: ...
    async def mark_jobs_as_processing(
        self, session: AsyncSession, job_ids: list[JobID]
    ) -> Sequence[DomainJob]: ...
    async def reset_stale_processing_jobs(
        self, session: AsyncSession, timeout_minutes: int
    ) -> None: ...
    async def mark_job_as_completed(
        self, session: AsyncSession, id: JobID, result: JobResult
    ) -> None: ...
    async def mark_job_as_failed(
        self, session: AsyncSession, id: JobID, processing_error: str | None = None
    ) -> None: ...
