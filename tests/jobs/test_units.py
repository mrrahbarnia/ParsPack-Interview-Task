import pytest
from uuid6 import uuid7

from src.modules.jobs.domain.models import Job as DomainJob, InvalidJobStatus
from src.modules.jobs import types


async def test_count_words_on_not_processing_job() -> None:

    job = DomainJob(
        id=types.JobID(uuid7()), text="sample text", status=types.JobStatus.PENDING
    )

    with pytest.raises(InvalidJobStatus):
        job.count_words()


async def test_count_unique_words_on_not_processing_job() -> None:

    job = DomainJob(
        id=types.JobID(uuid7()), text="sample text", status=types.JobStatus.PENDING
    )

    with pytest.raises(InvalidJobStatus):
        job.count_unique_words()


async def test_count_words() -> None:
    job = DomainJob(
        id=types.JobID(uuid7()), text="sample text", status=types.JobStatus.PROCESSING
    )
    word_numbers = job.count_words()

    assert word_numbers == 2


async def test_count_unique_words() -> None:
    job = DomainJob(
        id=types.JobID(uuid7()),
        text="sample sample sample text",
        status=types.JobStatus.PROCESSING,
    )
    word_numbers = job.count_unique_words()

    assert word_numbers == 2
