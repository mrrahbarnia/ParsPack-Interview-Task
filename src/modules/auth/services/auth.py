from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from .interfaces import IAuthRepo, IPasswordEncryptor
from ..types import UserID

from src.core.config import ENVS
from src.shared.service import Error


class AuthService:
    def __init__(
        self,
        repo: IAuthRepo,
        password_encryptor: IPasswordEncryptor,
        session_manager: async_sessionmaker[AsyncSession],
    ) -> None:
        self._repo = repo
        self._session_manager = session_manager
        self._password_encryptor = password_encryptor

    async def register(
        self, session: AsyncSession, username: str, password: str
    ) -> UserID | Error:
        encrypted_password = self._password_encryptor.encrypt(password)
        user_id = await self._repo.add(session, username, encrypted_password)
        if user_id is None:
            return Error.internal_error(message="Something went wrong")
        return user_id

    async def login(self, username: str, password: str) -> UserID | Error:
        if (username != ENVS.AUTH.DEFAULT_USERNAME) or (
            password != ENVS.AUTH.DEFAULT_PASSWORD
        ):
            return Error.not_found(entity="user", field_name="user", field_value="user")
        async with self._session_manager.begin() as session:
            user = await self._repo.get_by_username(session, username)
            if user is None:
                return await self.register(session, username, password)

            else:
                return user.id
