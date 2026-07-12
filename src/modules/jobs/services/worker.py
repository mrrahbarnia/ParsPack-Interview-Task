from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from .interfaces import IJobRepo

from src.core.config import ENVS
from src.shared.const import DBLock


class Worker:
    def __init__(
        self,
        repo: IJobRepo,
        session_manager: async_sessionmaker[AsyncSession],
    ) -> None:
        self._repo = repo
        self._session_manager = session_manager

    async def process_jobs(self) -> None:
        async with self._session_manager.begin() as session:
            ids = await self._repo.get_queued_job_ids(
                session=session,
                limit=ENVS.WORKER_POOL.JOBS_EXECUT_SIMULTANEOSLY,
                lock=DBLock(
                    is_active=True,
                    timeout_second=2,
                    skip_locked=True,
                ),
            )

            processing_jobs = await self._repo.mark_jobs_as_processing(
                session=session,
                job_ids=list(ids),
            )

        for job in processing_jobs:
            try:
                unique_words_count = job.count_unique_words()
                words_count = job.count_words()
                async with self._session_manager.begin() as session:
                    await self._repo.mark_job_as_completed(
                        session=session,
                        id=job.id,
                        result={
                            "unique_words": unique_words_count,
                            "word_count": words_count,
                        },
                    )

            except Exception as ex:
                async with self._session_manager.begin() as session:
                    await self._repo.mark_job_as_failed(
                        session=session,
                        id=job.id,
                        processing_error=str(ex),
                    )
