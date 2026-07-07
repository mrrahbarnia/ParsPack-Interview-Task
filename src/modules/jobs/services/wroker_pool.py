import asyncio

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from .interfaces import IJobRepo
from ..domain.models import Job as DomainJob


class JobWorkerPool:
    def __init__(
        self,
        *,
        worker_count: int,
        queue_size: int,
        repo: IJobRepo,
        session_manager: async_sessionmaker[AsyncSession],
    ) -> None:
        self._started = False
        self._queue: asyncio.Queue[DomainJob] = asyncio.Queue(maxsize=queue_size)
        self._workers: list[asyncio.Task[None]] = []

        self._repo = repo
        self._session_manager = session_manager
        self._worker_count = worker_count

    def start(self) -> None:
        if self._started:
            return

        self._started = True

        for _ in range(self._worker_count):
            task = asyncio.create_task(self._worker())
            self._workers.append(task)

    async def submit(self, job: DomainJob) -> None:
        await self._queue.put(job)

    async def _worker(self) -> None:
        while True:
            job = await self._queue.get()

            try:
                await self._execute(job)

            finally:
                self._queue.task_done()

    async def _execute(self, job: DomainJob) -> None:
        try:
            unique_words = await asyncio.to_thread(job.count_unique_words)

            word_count = await asyncio.to_thread(job.count_words)

            async with self._session_manager.begin() as session:
                await self._repo.mark_job_as_completed(
                    session=session,
                    id=job.id,
                    result={
                        "unique_words": unique_words,
                        "word_count": word_count,
                    },
                )

        except Exception as ex:
            async with self._session_manager.begin() as session:
                await self._repo.mark_job_as_failed(
                    session=session,
                    id=job.id,
                    processing_error=str(ex),
                )
