from ...infra import JobRepo
from ...services.worker_pool import JobWorkerPool

from src.core.config import ENVS


def get_repo() -> JobRepo:
    return JobRepo()


pool_instance = JobWorkerPool(
    worker_count=ENVS.WORKER_POOL.WORKER_COUNT,
    queue_size=ENVS.WORKER_POOL.JOBS_EXECUT_SIMULTANEOSLY,
    # I will pass them None and set them later in ./main.py
    repo=None,
    session_manager=None,
)


async def get_worker_pool() -> JobWorkerPool:
    pool_instance.start()

    return pool_instance
