import asyncio
import logging
import multiprocessing
from enum import StrEnum, auto

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from ..infra.repository import JobRepo
from ..types import JobID

from src.shared.const import DBLock
from src.shared.infra import SESSION_MAKER

logger = logging.getLogger(__name__)


class Control(StrEnum):
    STOP = auto()


class JobWorkerPool:
    def __init__(self, *, worker_count: int, queue_size: int) -> None:
        self._worker_count = worker_count
        self._queue: multiprocessing.Queue[JobID | object] = multiprocessing.Queue(
            maxsize=queue_size
        )
        self._processes: list[multiprocessing.Process] = []
        self._started = False

    def start(self) -> None:
        if self._started:
            return

        for i in range(self._worker_count):
            process = multiprocessing.Process(
                target=self._run_worker,
                name=f"worker-{i}",
                daemon=False,
            )

            process.start()
            self._processes.append(process)

        self._started = True

    def submit(self, job_id: JobID) -> None:
        if not self._started:
            logger.critical("Pool has not been started.")
            raise RuntimeError("Pool has not been started.")

        self._queue.put(job_id)

    def _run_worker(self) -> None:
        asyncio.run(self._worker_loop())

    async def _worker_loop(self) -> None:
        repo = JobRepo()
        while True:
            job_id = self._queue.get()

            if job_id == Control.STOP:
                return

            try:
                await self._execute(
                    job_id=job_id,  # type: ignore
                    session_maker=SESSION_MAKER,
                    repo=repo,
                )

            except Exception:
                import traceback

                traceback.print_exc()

    def stop(self) -> None:
        if not self._started:
            return

        for _ in self._processes:
            self._queue.put(Control.STOP)

        for p in self._processes:
            p.join()

        self._processes.clear()
        self._started = False

    async def _execute(
        self,
        job_id: JobID,
        session_maker: async_sessionmaker[AsyncSession],
        repo: JobRepo,
    ) -> None:
        async with session_maker.begin() as session:
            job = await repo.get_by_id(
                session=session, id=job_id, lock=DBLock(is_active=False)
            )
            if not job:
                logger.critical("Database error.")
                return

        try:
            unique_words = job.count_unique_words()
            word_count = job.count_words()

            async with session_maker.begin() as session:
                await repo.mark_job_as_completed(
                    session=session,
                    id=job.id,
                    result={
                        "unique_words": unique_words,
                        "word_count": word_count,
                    },
                )

        except Exception as ex:
            async with session_maker.begin() as session:
                await repo.mark_job_as_failed(
                    session=session,
                    id=job.id,
                    processing_error=str(ex),
                )
