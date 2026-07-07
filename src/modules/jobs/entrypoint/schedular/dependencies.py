from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from ...infra import JobRepo
from ...services.wroker_pool import JobWorkerPool

from src.core.config import ENVS
from src.shared.infra import SESSION_MAKER


def get_session_maker() -> async_sessionmaker[AsyncSession]:
    return SESSION_MAKER


def get_repo() -> JobRepo:
    return JobRepo()


# TODO: Read variables from .env
pool_instance = JobWorkerPool(
    worker_count=ENVS.WORKER_POOL.WORKER_COUNT,
    queue_size=ENVS.WORKER_POOL.JOBS_EXECUT_SIMULTANEOSLY,
    repo=get_repo(),
    session_manager=SESSION_MAKER,
)


async def get_worker_pool() -> JobWorkerPool:
    pool_instance.start()
    return pool_instance
