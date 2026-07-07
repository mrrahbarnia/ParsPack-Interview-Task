from datetime import datetime

import sqlalchemy as sa
import sqlalchemy.orm as so
from uuid6 import uuid7
from sqlalchemy.dialects.postgresql import JSONB

from ..types import JobID, JobStatus, JobResult

from src.shared.infra import BaseModel


class Job(BaseModel):
    __tablename__ = "jobs"
    processing_error: so.Mapped[str | None] = so.mapped_column(sa.Text)
    start_processing_at: so.Mapped[datetime | None]
    result: so.Mapped[JobResult | None] = so.mapped_column(JSONB)
    text: so.Mapped[str] = so.mapped_column(sa.Text, unique=True)
    status: so.Mapped[JobStatus] = so.mapped_column(default=JobStatus.PENDING)
    created_at: so.Mapped[datetime] = so.mapped_column(default=lambda: datetime.now())
    updated_at: so.Mapped[datetime] = so.mapped_column(
        default=lambda: datetime.now(), onupdate=lambda: datetime.now()
    )
    id: so.Mapped[JobID] = so.mapped_column(primary_key=True, default=lambda: uuid7())
