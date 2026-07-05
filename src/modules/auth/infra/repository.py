import sqlalchemy as sa

from sqlalchemy.ext.asyncio import AsyncSession

from .db_models import User


class AuthRepo:
    def __init__(self) -> None:
        pass

    async def get_by_username(
        self, session: AsyncSession, username: str
    ) -> User | None:
        stmt = sa.select(User).where(User.username == username).limit(1)
        user = await session.scalar(stmt)
        return user

    async def add(
        self, session: AsyncSession, username: str, hashed_password: str
    ) -> None:
        stmt = sa.insert(User).values(
            {User.username: username, User.hashed_password: hashed_password}
        )
        await session.execute(stmt)
