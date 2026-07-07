from pydantic_settings import BaseSettings


class WorkerPool(BaseSettings):
    WORKER_COUNT: int
    JOBS_EXECUT_SIMULTANEOSLY: int
