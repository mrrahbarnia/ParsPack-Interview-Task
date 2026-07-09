import asyncio
import logging
import traceback
from typing import Annotated

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from aioclock import AioClock, Every, Depends

from . import dependencies as dc
from ...infra import JobRepo
from ...services.scheduler import JobScheduler
from ...services.worker_pool import JobWorkerPool

from src.shared.entrypoint.dependencies import get_session_maker

logger = logging.getLogger(__name__)

app = AioClock()


@app.task(trigger=Every(seconds=1))  # type: ignore
async def execute_jobs(
    session_maker: Annotated[
        async_sessionmaker[AsyncSession], Depends(get_session_maker)
    ],
    repo: Annotated[JobRepo, Depends(dc.get_repo)],
    worker_pool: Annotated[JobWorkerPool, Depends(dc.get_worker_pool)],
) -> None:
    try:
        worker_pool.repo = repo
        worker_pool.session_manager = session_maker
        await JobScheduler(
            repo=repo, session_manager=session_maker, pool=worker_pool
        ).execute_pending_jobs()
    except Exception:
        logger.critical(traceback.format_exc())


if __name__ == "__main__":
    asyncio.run(app.serve())
