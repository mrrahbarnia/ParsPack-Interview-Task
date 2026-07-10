from pydantic_settings import BaseSettings


class Schedular(BaseSettings):
    PROCESSING_JOB_TIMEOUT_MINUTES: int
    RESTORE_STALE_PROCEESING_JOBS_INTERVAL_SEC: int
    PROCESSING_PENDING_JOBS_INTERVAL_SECONDS: int
