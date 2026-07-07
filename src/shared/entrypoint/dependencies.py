from typing import Annotated

from fastapi import Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.modules.auth.types import UserID
from src.modules.auth.infra import JWT_INSTANCE

security = HTTPBearer(auto_error=True)


class InvalidToken(Exception): ...


def get_authenticated_user_id(
    credentials: Annotated[HTTPAuthorizationCredentials, Security(security)],
) -> UserID:
    token = credentials.credentials

    payload = JWT_INSTANCE.verify_token(token)

    if payload is None:
        raise InvalidToken

    return payload.get("user_id")
