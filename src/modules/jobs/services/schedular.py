from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from .interfaces import IJobRepo

from src.core.config import ENVS
from src.shared.const import DBLock


class JobScheduler:
    def __init__(
        self,
        repo: IJobRepo,
        session_manager: async_sessionmaker[AsyncSession],
    ) -> None:
        self._repo = repo
        self._session_manager = session_manager

    async def queue_pending_jobs(self) -> None:

        async with self._session_manager.begin() as session:
            ids = await self._repo.get_pending_job_ids(
                session=session,
                limit=ENVS.WORKER_POOL.JOBS_EXECUT_SIMULTANEOSLY,
                lock=DBLock(
                    is_active=True,
                    timeout_second=2,
                    skip_locked=True,
                ),
            )

            await self._repo.mark_jobs_as_queued(
                session=session,
                job_ids=list(ids),
            )

    async def reset_stale_processing_jobs(self) -> None:
        async with self._session_manager.begin() as session:
            await self._repo.reset_stale_processing_jobs(
                session=session,
                timeout_minutes=ENVS.SCHEDULAR.PROCESSING_JOB_TIMEOUT_MINUTES,
            )

    async def reset_stale_queued_jobs(self) -> None:
        async with self._session_manager.begin() as session:
            await self._repo.reset_stale_queued_jobs(
                session=session,
                timeout_minutes=ENVS.SCHEDULAR.PROCESSING_JOB_TIMEOUT_MINUTES,
            )
