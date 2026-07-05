from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from ....infra import BcryptPasswordEncryptor, AuthRepo

from src.shared.infra import SESSION_MAKER


async def get_session_maker() -> async_sessionmaker[AsyncSession]:
    return SESSION_MAKER


async def get_password_encryptor() -> BcryptPasswordEncryptor:
    return BcryptPasswordEncryptor()


async def get_repo() -> AuthRepo:
    return AuthRepo()
