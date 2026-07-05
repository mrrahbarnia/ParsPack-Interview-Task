import typing as T

from fastapi import HTTPException

from src.core.config import ENVS

from ..const import Environment


class AppBaseException(HTTPException):
    def __init__(
        self,
        *,
        message: str,
        success: bool,
        status_code: int,
        data: T.Any | None = None,
    ):
        if (ENVS.ENVIRONMENT == Environment.PRODUCTION) and (status_code >= 500):
            self.data = None
        else:
            self.data = str(data)

        self.message = message
        self.status_code = status_code
        self.success = success
        super().__init__(status_code=status_code)
