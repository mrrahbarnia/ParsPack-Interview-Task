from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from ....infra import JobRepo

from src.shared.infra import SESSION_MAKER


async def get_session_maker() -> async_sessionmaker[AsyncSession]:
    return SESSION_MAKER


async def get_repo() -> JobRepo:
    return JobRepo()
