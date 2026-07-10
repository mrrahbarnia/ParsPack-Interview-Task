from uuid6 import uuid7
import sqlalchemy as sa
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.modules.jobs.infra.db_models import Job as DBJob
from src.modules.jobs.types import JobStatus


async def test_create_job_successfully(
    authenticated_async_client: AsyncClient,
    test_session_maker: async_sessionmaker[AsyncSession],
) -> None:
    url = "/jobs"

    payload = {"text": " sample text "}

    resp = await authenticated_async_client.post(url=url, json=payload)
    body = resp.json()

    stmt = sa.select(DBJob).where(DBJob.id == body["data"]["job_id"])
    async with test_session_maker.begin() as session:
        job = await session.scalar(stmt)

    assert resp.status_code == 201
    assert body["success"] is True
    assert body["message"] == "Job created successfully."
    assert body["data"]["job_id"]
    assert job is not None
    assert job.text == "sample text"
    assert job.status == JobStatus.PENDING


async def test_create_duplicate_jobs(
    authenticated_async_client: AsyncClient,
    test_session_maker: async_sessionmaker[AsyncSession],
) -> None:
    url = "/jobs"

    payload = {"text": "duplicate text"}

    await authenticated_async_client.post(url=url, json=payload)

    duplicate_resp = await authenticated_async_client.post(url=url, json=payload)

    stmt = sa.select(sa.func.count()).select_from(DBJob)
    async with test_session_maker.begin() as session:
        row_numbers = await session.scalar(stmt)

    assert duplicate_resp.status_code == 201
    assert row_numbers == 1


async def test_get_pending_job_successfully(
    authenticated_async_client: AsyncClient,
) -> None:
    create_resp = await authenticated_async_client.post(
        url="/jobs",
        json={"text": "pending job text"},
    )
    job_id = create_resp.json()["data"]["job_id"]

    resp = await authenticated_async_client.get(url=f"/jobs/{job_id}")
    body = resp.json()

    assert resp.status_code == 200
    assert body["success"] is True
    assert body["message"] == "Job result fetched successfully."
    assert body["data"] == {"status": "pending", "result": None}


async def test_get_completed_job_successfully(
    authenticated_async_client: AsyncClient,
    test_session_maker: async_sessionmaker[AsyncSession],
) -> None:
    result = {"word_count": 3, "unique_words": 2}
    stmt = (
        sa.insert(DBJob)
        .values(
            {
                DBJob.text: "completed completed job",
                DBJob.status: JobStatus.COMPLETED,
                DBJob.result: result,
            }
        )
        .returning(DBJob.id)
    )
    async with test_session_maker.begin() as session:
        job_id = await session.scalar(stmt)

    resp = await authenticated_async_client.get(url=f"/jobs/{job_id}")
    body = resp.json()

    assert resp.status_code == 200
    assert body["data"] == {"status": "completed", "result": result}


async def test_get_missing_job_returns_not_found(
    authenticated_async_client: AsyncClient,
) -> None:
    missing_job_id = uuid7()

    resp = await authenticated_async_client.get(url=f"/jobs/{missing_job_id}")
    body = resp.json()

    assert resp.status_code == 404
    assert body["success"] is False
    assert body["message"] == f"job with id {missing_job_id} not found"


async def test_get_job_with_invalid_id_returns_validation_error(
    authenticated_async_client: AsyncClient,
) -> None:
    resp = await authenticated_async_client.get(url="/jobs/not-a-uuid")

    assert resp.status_code == 422


async def test_create_job_without_token_returns_forbidden(
    async_client: AsyncClient,
) -> None:
    resp = await async_client.post(url="/jobs", json={"text": "protected"})

    assert resp.status_code == 401


async def test_create_job_with_invalid_token_returns_unauthorized(
    async_client: AsyncClient,
) -> None:
    resp = await async_client.post(
        url="/jobs",
        json={"text": "protected"},
        headers={"Authorization": "Bearer invalid-token"},
    )
    body = resp.json()

    assert resp.status_code == 401
    assert body == {
        "success": False,
        "message": "Unauthorized.",
        "data": {"reason": "InvalidToken"},
    }


async def test_create_job_with_missing_text_returns_validation_error(
    authenticated_async_client: AsyncClient,
) -> None:
    resp = await authenticated_async_client.post(url="/jobs", json={})

    assert resp.status_code == 422
