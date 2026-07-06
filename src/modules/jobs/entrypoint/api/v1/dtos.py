from pydantic import BaseModel

from ....types import JobID

from src.shared.utils import StrippedStr


class JobCreateRequest(BaseModel):
    text: StrippedStr


class JobCreateResponse(BaseModel):
    job_id: JobID
