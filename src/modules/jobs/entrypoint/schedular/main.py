import asyncio
import logging
import traceback
from typing import Annotated, AsyncGenerator

from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from aioclock import AioClock, Every, Group, Depends

from . import dependencies as dc
from ...infra import JobRepo
from ...services.schedular import JobScheduler
from ...services.worker_pool import JobWorkerPool

from src.core.config import ENVS
from src.shared.entrypoint.dependencies import get_session_maker

logger = logging.getLogger(__name__)


group = Group()

worker_pool: JobWorkerPool | None = None


@group.task(  # type: ignore
    trigger=Every(seconds=ENVS.SCHEDULAR.PROCESSING_PENDING_JOBS_INTERVAL_SECONDS)
)
async def execute_jobs(
    session_maker: Annotated[
        async_sessionmaker[AsyncSession], Depends(get_session_maker)
    ],
    repo: Annotated[JobRepo, Depends(dc.get_repo)],
) -> None:
    if worker_pool is None:
        raise RuntimeError("Worker pool didnt start yet.")
    try:
        await JobScheduler(
            repo=repo, session_manager=session_maker, pool=worker_pool
        ).execute_pending_jobs()

    except Exception:
        logger.critical(traceback.format_exc())


@group.task(  # type: ignore
    trigger=Every(seconds=ENVS.SCHEDULAR.RESTORE_STALE_PROCEESING_JOBS_INTERVAL_SEC)
)
async def reset_stale_processing_jobs(
    session_maker: Annotated[
        async_sessionmaker[AsyncSession], Depends(get_session_maker)
    ],
    repo: Annotated[JobRepo, Depends(dc.get_repo)],
) -> None:
    if worker_pool is None:
        raise RuntimeError("Worker pool didnt start yet.")
    try:
        await JobScheduler(
            repo=repo, session_manager=session_maker, pool=worker_pool
        ).reset_stale_processing_jobs()

    except Exception:
        logger.critical(traceback.format_exc())


@asynccontextmanager
async def lifespan(aio_clock: AioClock) -> AsyncGenerator[AioClock]:
    global worker_pool
    pool_instance = JobWorkerPool(
        worker_count=ENVS.WORKER_POOL.WORKER_COUNT,
        queue_size=ENVS.WORKER_POOL.JOBS_EXECUT_SIMULTANEOSLY,
    )
    pool_instance.start()
    worker_pool = pool_instance

    yield aio_clock

    await pool_instance.stop()


app = AioClock(lifespan=lifespan)
app.include_group(group)


if __name__ == "__main__":
    asyncio.run(app.serve())
