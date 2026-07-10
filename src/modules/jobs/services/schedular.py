from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from .worker_pool import JobWorkerPool
from .interfaces import IJobRepo

from src.core.config import ENVS
from src.shared.const import DBLock


class JobScheduler:
    def __init__(
        self,
        repo: IJobRepo,
        session_manager: async_sessionmaker[AsyncSession],
        pool: JobWorkerPool,
    ):
        self._repo = repo
        self._session_manager = session_manager
        self._pool = pool

    async def execute_pending_jobs(self) -> None:

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

            jobs = await self._repo.mark_jobs_as_processing(
                session=session,
                job_ids=list(ids),
            )

        for job in jobs:
            await self._pool.submit(job)

    async def reset_stale_processing_jobs(self) -> None:
        async with self._session_manager.begin() as session:
            await self._repo.reset_stale_processing_jobs(
                session=session,
                timeout_minutes=ENVS.SCHEDULAR.PROCESSING_JOB_TIMEOUT_MINUTES,
            )
