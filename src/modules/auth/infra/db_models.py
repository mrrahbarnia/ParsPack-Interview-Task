from datetime import datetime

import sqlalchemy as sa
import sqlalchemy.orm as so

from uuid6 import uuid7

from ..types import UserID

from src.shared.infra import BaseModel


class User(BaseModel):
    __tablename__ = "users"
    hashed_password: so.Mapped[str] = so.mapped_column(sa.String(255))
    username: so.Mapped[str] = so.mapped_column(sa.String(255), unique=True)
    created_at: so.Mapped[datetime] = so.mapped_column(default=lambda: datetime.now())
    id: so.Mapped[UserID] = so.mapped_column(primary_key=True, default=lambda: uuid7())
