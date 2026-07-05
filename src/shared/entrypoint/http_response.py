import typing as T

from pydantic import BaseModel

V = T.TypeVar("V")


class HTTPResponse(BaseModel, T.Generic[V]):
    success: bool
    message: str
    data: V | None = None
