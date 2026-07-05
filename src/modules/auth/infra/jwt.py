from typing import Any
from datetime import datetime, timedelta, UTC

import jwt

from .. import types

from src.core.config import ENVS


class JWTService:
    def __init__(
        self, secret_key: str, algorithm: str, access_token_expires_minute: int
    ) -> None:
        self._secret_key = secret_key
        self._algorithm = algorithm
        self._access_token_expires_minute = access_token_expires_minute

    def create_access_token(
        self,
        token_payload: types.TokenPayload,
    ) -> str:
        expires_delta = timedelta(minutes=self._access_token_expires_minute)

        now = datetime.now(UTC)

        expire_time = now + expires_delta

        payload: dict[str, Any] = {
            "user_id": str(token_payload["user_id"]),
            "iat": now,
            "exp": expire_time,
            "type": "access",
        }

        return jwt.encode(  # # type: ignore[misc]
            payload=payload,
            key=self._secret_key,
            algorithm=self._algorithm,
        )

    def verify_token(self, token: str) -> types.TokenPayload | None:
        try:
            decoded = jwt.decode(  # # type: ignore[misc]
                token,
                self._secret_key,
                algorithms=[self._algorithm],
                options={
                    "verify_signature": True,
                    "verify_exp": True,
                },
            )

            payload = types.TokenPayload(
                user_id=decoded["user_id"],
            )

            return payload

        except jwt.ExpiredSignatureError:
            print("Token has expired")
            return None
        except jwt.InvalidTokenError as e:
            print(f"Invalid token: {e}")
            return None


JWT_INSTANCE = JWTService(
    secret_key=ENVS.JWT.SECRET_KEY,
    algorithm=ENVS.JWT.ALGORITHM,
    access_token_expires_minute=ENVS.JWT.ACCESS_TOKEN_EXPIRES_MINUTE,
)
