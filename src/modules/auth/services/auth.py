from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from .interfaces import IAuthRepo, IPasswordEncryptor

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
    ) -> None:
        encrypted_password = self._password_encryptor.encrypt(password)
        print("{encrypted_password=}")
        await self._repo.add(session, username, encrypted_password)

    async def login(self, username: str, password: str) -> str | Error:
        if (username != ENVS.AUTH.DEFAULT_USERNAME) or (
            password != ENVS.AUTH.DEFAULT_PASSWORD
        ):
            return Error.not_found(entity="user", field_name="user", field_value="user")
        async with self._session_manager.begin() as session:
            user = await self._repo.get_by_username(session, username)
            if user is None:
                await self.register(session, username, password)

        return "OK"
