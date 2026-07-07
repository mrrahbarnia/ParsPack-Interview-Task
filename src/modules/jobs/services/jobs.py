from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from .interfaces import IJobRepo
from ..types import JobID
from ..domain.models import Job as DomainJob

from src.shared.service import Error
from src.shared.const import DBLock


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

    async def get_job_by_id(self, job_id: JobID) -> DomainJob | Error:
        async with self._session_manager.begin() as session:
            job = await self._repo.get_by_id(
                session=session, id=job_id, lock=DBLock(is_active=False)
            )

        if not job:
            return Error.not_found(entity="job", field_name="id", field_value=job_id)

        return job
