from pydantic_settings import BaseSettings, SettingsConfigDict

from . import schemas

from src.shared.const import Environment


class _ENVS(BaseSettings):
    model_config = SettingsConfigDict(
        env_nested_delimiter="__",
        env_file=".env",
    )
    ENVIRONMENT: Environment
    POSTGRESQL: schemas.PostgreSQL
    FASTAPI: schemas.FastAPI
    AUTH: schemas.Auth
    JWT: schemas.JWT
    WORKER_POOL: schemas.WorkerPool


ENVS = _ENVS()  # type: ignore
