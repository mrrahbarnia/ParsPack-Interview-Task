import asyncio
import logging
import traceback
from typing import Annotated

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from aioclock import AioClock, Every, Depends

from . import dependencies as dc
from ...infra import JobRepo
from ...services.worker import Worker

from src.core.config import ENVS
from src.shared.entrypoint.dependencies import get_session_maker

logger = logging.getLogger(__name__)


app = AioClock()


@app.task(  # type: ignore
    trigger=Every(seconds=ENVS.SCHEDULAR.PROCESSING_PENDING_JOBS_INTERVAL_SECONDS)
)
async def schedule_worker(
    session_maker: Annotated[
        async_sessionmaker[AsyncSession], Depends(get_session_maker)
    ],
    repo: Annotated[JobRepo, Depends(dc.get_repo)],
) -> None:
    try:
        await Worker(
            repo=repo,
            session_manager=session_maker,
        ).process_jobs()

    except Exception:
        logger.critical(traceback.format_exc())


if __name__ == "__main__":
    asyncio.run(app.serve())
