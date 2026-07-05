from typing import Protocol
from sqlalchemy.ext.asyncio import AsyncSession

from ..infra.db_models import User


class IAuthRepo(Protocol):
    async def get_by_username(
        self, session: AsyncSession, username: str
    ) -> User | None: ...

    async def add(
        self, session: AsyncSession, username: str, hashed_password: str
    ) -> None: ...


class IPasswordEncryptor(Protocol):
    def encrypt(self, password: str) -> str: ...

    def verify(self, password: str, encrypted: str) -> bool: ...
