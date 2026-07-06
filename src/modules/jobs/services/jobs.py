from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from .interfaces import IJobRepo
from ..types import JobID

from src.shared.service import Error


class JobService:
    def __init__(
        self, repo: IJobRepo, session_manager: async_sessionmaker[AsyncSession]
    ) -> None:
        self._repo = repo
        self._session_manager = session_manager

    async def create(self, text: str) -> JobID | Error:
        async with self._session_manager.begin() as session:
            if job_id := await self._repo.get_id_by_text(session, text):
                return job_id

            job_id = await self._repo.add(session, text)
            if not job_id:
                return Error.internal_error(details="Database internal error.")

        return job_id
