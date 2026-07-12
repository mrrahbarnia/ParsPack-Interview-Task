import asyncio
import logging
import traceback
from typing import Annotated

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from aioclock import AioClock, Every, Depends

from . import dependencies as dc
from ...infra import JobRepo
from ...services.schedular import JobScheduler

from src.core.config import ENVS
from src.shared.entrypoint.dependencies import get_session_maker

logger = logging.getLogger(__name__)


app = AioClock()


@app.task(  # type: ignore
    trigger=Every(seconds=ENVS.SCHEDULAR.PROCESSING_PENDING_JOBS_INTERVAL_SECONDS)
)
async def queued_pending_jobs(
    session_maker: Annotated[
        async_sessionmaker[AsyncSession], Depends(get_session_maker)
    ],
    repo: Annotated[JobRepo, Depends(dc.get_repo)],
) -> None:
    try:
        await JobScheduler(
            repo=repo, session_manager=session_maker
        ).queue_pending_jobs()

    except Exception:
        logger.critical(traceback.format_exc())


@app.task(  # type: ignore
    trigger=Every(seconds=ENVS.SCHEDULAR.RESTORE_STALE_PROCEESING_JOBS_INTERVAL_SEC)
)
async def reset_stale_queued_jobs(
    session_maker: Annotated[
        async_sessionmaker[AsyncSession], Depends(get_session_maker)
    ],
    repo: Annotated[JobRepo, Depends(dc.get_repo)],
) -> None:
    try:
        await JobScheduler(
            repo=repo, session_manager=session_maker
        ).reset_stale_queued_jobs()

    except Exception:
        logger.critical(traceback.format_exc())


@app.task(  # type: ignore
    trigger=Every(seconds=ENVS.SCHEDULAR.RESTORE_STALE_PROCEESING_JOBS_INTERVAL_SEC)
)
async def reset_stale_processing_jobs(
    session_maker: Annotated[
        async_sessionmaker[AsyncSession], Depends(get_session_maker)
    ],
    repo: Annotated[JobRepo, Depends(dc.get_repo)],
) -> None:
    try:
        await JobScheduler(
            repo=repo, session_manager=session_maker
        ).reset_stale_processing_jobs()

    except Exception:
        logger.critical(traceback.format_exc())


if __name__ == "__main__":
    asyncio.run(app.serve())
