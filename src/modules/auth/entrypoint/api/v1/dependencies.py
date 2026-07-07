from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from ....infra import BcryptPasswordEncryptor, AuthRepo, JWTService, JWT_INSTANCE

from src.shared.infra import SESSION_MAKER


def get_jwt_service() -> JWTService:
    return JWT_INSTANCE


def get_session_maker() -> async_sessionmaker[AsyncSession]:
    return SESSION_MAKER


def get_password_encryptor() -> BcryptPasswordEncryptor:
    return BcryptPasswordEncryptor()


def get_repo() -> AuthRepo:
    return AuthRepo()
