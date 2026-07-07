from pydantic import BaseModel

from ....types import JobID, JobStatus, JobResult

from src.shared.utils import StrippedStr


class JobCreateRequest(BaseModel):
    text: StrippedStr


class JobCreateResponse(BaseModel):
    job_id: JobID


class JobDetailResponse(BaseModel):
    status: JobStatus
    result: JobResult | None = None
