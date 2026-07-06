from typing import Protocol

from sqlalchemy.ext.asyncio import AsyncSession

from ..types import JobID


class IJobRepo(Protocol):
    async def get_id_by_text(
        self, session: AsyncSession, text: str
    ) -> JobID | None: ...
    async def add(self, session: AsyncSession, text: str) -> JobID | None: ...
