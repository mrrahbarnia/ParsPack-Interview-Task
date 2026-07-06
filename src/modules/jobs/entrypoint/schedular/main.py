import asyncio
import logging
import traceback
from typing import Annotated

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from aioclock import AioClock, Every, Depends


from . import dependencies as dc
from ...infra import JobRepo
from ...services import JobService

logger = logging.getLogger(__name__)

app = AioClock()


@app.task(trigger=Every(seconds=1))  # type: ignore
async def execute_jobs(
    session_maker: Annotated[
        async_sessionmaker[AsyncSession], Depends(dc.get_session_maker)
    ],
    repo: Annotated[JobRepo, Depends(dc.get_repo)],
) -> None:
    try:
        await JobService(repo, session_maker).execute_pending_jobs()
    except Exception:
        logger.critical(traceback.format_exc())


if __name__ == "__main__":
    asyncio.run(app.serve())
