import logging
import typing as T
from contextlib import asynccontextmanager
from logging.config import dictConfig

from fastapi import FastAPI

from .logger import LogConfig


logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_application: FastAPI) -> T.AsyncGenerator[None, None]:
    # ============================== On startup
    logger.info("Logger is running...")
    dictConfig(LogConfig().model_dump())

    logger.info("Application is running...")

    yield
    # ============================== On shutdown

    logger.info("Application is shutting down...")
