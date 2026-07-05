from datetime import datetime

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase, MappedAsDataclass
from sqlalchemy.types import DateTime

from src.core.config import ENVS

ASYNC_ENGINE: AsyncEngine = create_async_engine(ENVS.POSTGRESQL.get_url)

SESSION_MAKER: async_sessionmaker[AsyncSession] = async_sessionmaker(
    ASYNC_ENGINE, expire_on_commit=False
)


class BaseModel(DeclarativeBase, MappedAsDataclass):
    type_annotation_map = {
        datetime: DateTime(timezone=True),
    }
