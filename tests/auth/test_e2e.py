import sqlalchemy as sa
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.core.config import ENVS
from src.modules.auth.infra.db_models import User as DBUser


async def test_login_successfully(
    async_client: AsyncClient,
) -> None:
    resp = await async_client.post(
        url="/auth/login",
        json={
            "username": ENVS.AUTH.DEFAULT_USERNAME,
            "password": ENVS.AUTH.DEFAULT_PASSWORD,
        },
    )

    body = resp.json()

    assert resp.status_code == 200
    assert body["success"] is True
    assert body["message"] == "Logged in successfully."
    assert body["data"]["token_type"] == "bearer"
    assert body["data"]["access_token"]


async def test_login_creates_only_one_default_user(
    async_client: AsyncClient,
    test_session_maker: async_sessionmaker[AsyncSession],
) -> None:
    payload = {
        "username": ENVS.AUTH.DEFAULT_USERNAME,
        "password": ENVS.AUTH.DEFAULT_PASSWORD,
    }

    first_resp = await async_client.post(url="/auth/login", json=payload)
    second_resp = await async_client.post(url="/auth/login", json=payload)

    stmt = sa.select(sa.func.count()).select_from(DBUser)
    async with test_session_maker.begin() as session:
        user_count = await session.scalar(stmt)

    assert first_resp.status_code == 200
    assert second_resp.status_code == 200
    assert user_count == 1


async def test_login_with_invalid_credentials_returns_not_found(
    async_client: AsyncClient,
) -> None:
    resp = await async_client.post(
        url="/auth/login",
        json={"username": "wrong", "password": "wrong"},
    )

    body = resp.json()

    assert resp.status_code == 404
    assert body["success"] is False
    assert body["message"] == "user with user user not found"


async def test_login_with_missing_payload_field_returns_validation_error(
    async_client: AsyncClient,
) -> None:
    resp = await async_client.post(
        url="/auth/login",
        json={"username": ENVS.AUTH.DEFAULT_USERNAME},
    )

    assert resp.status_code == 422
