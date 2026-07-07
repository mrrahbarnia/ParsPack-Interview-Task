from typing import Generator, Any, AsyncGenerator

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from testcontainers.keycloak import DockerContainer  # type: ignore
from testcontainers.core.waiting_utils import wait_for_logs  # type: ignore

from src.core.setup import application
from src.core.config import ENVS
from src.shared.infra import BaseModel
from src.shared.entrypoint.dependencies import get_session_maker


@pytest.fixture(scope="session")
def pg_container() -> Generator[DockerContainer, Any, None]:
    container = (
        DockerContainer("postgres:17.4")
        .with_env("POSTGRES_USER", "admin")
        .with_env("POSTGRES_PASSWORD", "admin")
        .with_env("POSTGRES_DB", "db")
        .with_exposed_ports(5432)
    )
    container.start()
    wait_for_logs(
        container, "database system is ready to accept connections", timeout=60
    )
    try:
        yield container
    finally:
        container.stop()


@pytest_asyncio.fixture
async def test_session_maker(
    pg_container: DockerContainer,
) -> AsyncGenerator[async_sessionmaker[AsyncSession], Any]:
    engine = create_async_engine(
        url=f"postgresql+asyncpg://admin:admin@{pg_container.get_container_host_ip()}:{pg_container.get_exposed_port(5432)}/db"
    )
    test_session_maker = async_sessionmaker(engine, expire_on_commit=False)
    async with engine.begin() as conn:
        await conn.run_sync(BaseModel.metadata.drop_all)
        await conn.run_sync(BaseModel.metadata.create_all)

    application.dependency_overrides[get_session_maker] = lambda: test_session_maker

    try:
        yield test_session_maker
    finally:
        await engine.dispose()


@pytest_asyncio.fixture
async def async_client(
    test_session_maker: AsyncGenerator[async_sessionmaker[AsyncSession], Any],
) -> AsyncGenerator[AsyncClient, Any]:
    transport = ASGITransport(app=application)
    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:
        yield client


@pytest_asyncio.fixture
async def authenticated_async_client(async_client: AsyncClient) -> AsyncClient:
    url = "/auth/login"

    payload = {
        "username": ENVS.AUTH.DEFAULT_USERNAME,
        "password": ENVS.AUTH.DEFAULT_PASSWORD,
    }
    resp = await async_client.post(url=url, json=payload)

    access_token = resp.json().get("data", {}).get("access_token")
    assert access_token

    async_client.headers.update({"Authorization": f"Bearer {access_token}"})
    return async_client
