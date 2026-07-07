import sqlalchemy as sa
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.modules.jobs.infra.db_models import Job as DBJob


async def test_create_job_successfully(
    authenticated_async_client: AsyncClient,
) -> None:
    url = "/jobs"

    payload = {"text": "sample text"}

    resp = await authenticated_async_client.post(url=url, json=payload)

    assert resp.status_code == 201
    assert "job_id" in resp.json()["data"]


async def test_create_duplicate_jobs(
    authenticated_async_client: AsyncClient,
    test_session_maker: async_sessionmaker[AsyncSession],
) -> None:
    url = "/jobs"

    payload = {"text": "duplicate text"}

    await authenticated_async_client.post(url=url, json=payload)

    await authenticated_async_client.post(url=url, json=payload)

    stmt = sa.select(sa.func.count()).select_from(DBJob)
    async with test_session_maker.begin() as session:
        row_numbers = await session.scalar(stmt)

    assert row_numbers == 1
