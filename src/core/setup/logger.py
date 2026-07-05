from pydantic import BaseModel

from src.core.config import ENVS


class LogConfig(BaseModel):
    version: int = 1
    disable_existing_loggers: bool = False
    formatters: dict[str, dict[str, str]] = {
        "console": {
            "format": '{"time":"%(asctime)s", "name": "%(name)s", "level": "%(levelname)s","function": "%(funcName)s", "message": "%(message)s"}',
            "datefmt": "%Y-%m-%dT%H:%M:%SZ",
        },
        "json": {
            "()": "pythonjsonlogger.json.JsonFormatter",
            "fmt": '{"time":"%(asctime)s", "name": "%(name)s", "level": "%(levelname)s","function": "%(funcName)s", "message": "%(message)s"}',
            "datefmt": "%Y-%m-%dT%H:%M:%SZ",
        },
    }
    handlers: dict[str, dict[str, str | int]] = {
        "json": {
            "class": "logging.StreamHandler",
            "level": ENVS.FASTAPI.LOG_LEVEL,
            "formatter": "json",
        },
    }
