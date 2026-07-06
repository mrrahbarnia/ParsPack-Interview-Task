from typing import NewType
from uuid import UUID
from enum import StrEnum, auto

JobID = NewType("JobID", UUID)


class JobStatus(StrEnum):
    PENDING = auto()
    PROCESSING = auto()
    COMPLETED = auto()
    FAILED = auto()
