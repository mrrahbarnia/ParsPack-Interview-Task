from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from ...infra import JobRepo
from ...services.wroker_pool import JobWorkerPool

from src.shared.infra import SESSION_MAKER


def get_session_maker() -> async_sessionmaker[AsyncSession]:
    return SESSION_MAKER


def get_repo() -> JobRepo:
    return JobRepo()


# TODO: Read variables from .env
pool_instance = JobWorkerPool(
    worker_count=4,
    queue_size=100,
    repo=get_repo(),
    session_manager=SESSION_MAKER,
)


async def get_worker_pool() -> JobWorkerPool:
    pool_instance.start()
    return pool_instance
