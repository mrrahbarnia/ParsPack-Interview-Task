from typing import NewType, TypedDict
from uuid import UUID
from enum import StrEnum, auto

JobID = NewType("JobID", UUID)


class JobStatus(StrEnum):
    PENDING = auto()
    QUEUED = auto()
    PROCESSING = auto()
    COMPLETED = auto()
    FAILED = auto()


class JobResult(TypedDict):
    word_count: int
    unique_words: int
