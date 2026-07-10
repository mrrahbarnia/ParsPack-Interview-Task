from datetime import datetime, timedelta, UTC

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.core.config import ENVS
from src.modules.jobs.infra import JobRepo
from src.modules.jobs.infra.db_models import Job as DBJob
from src.modules.jobs.services.schedular import JobScheduler
from src.modules.jobs.services.worker_pool import JobWorkerPool
from src.modules.jobs.types import JobStatus


async def test_execute_pending_jobs_on_pool_to_complete_jobs(
    test_session_maker: async_sessionmaker[AsyncSession],
) -> None:
    repo = JobRepo()
    pool = JobWorkerPool(
        worker_count=1,
        queue_size=1,
        repo=repo,
        session_manager=test_session_maker,
    )
    scheduler = JobScheduler(
        repo=repo,
        session_manager=test_session_maker,
        pool=pool,
    )
    stmt = (
        sa.insert(DBJob)
        .values({DBJob.text: "hello hello scheduler"})
        .returning(DBJob.id)
    )
    async with test_session_maker.begin() as session:
        job_id = await session.scalar(stmt)

    pool.start()
    await scheduler.execute_pending_jobs()
    await pool.stop()

    select_stmt = sa.select(DBJob).where(DBJob.id == job_id)
    async with test_session_maker.begin() as session:
        job = await session.scalar(select_stmt)

    assert job is not None
    assert job.status == JobStatus.COMPLETED
    assert job.result == {"unique_words": 2, "word_count": 3}


async def test_reset_stale_processing_jobs_only_resets_stale_processing_jobs(
    test_session_maker: async_sessionmaker[AsyncSession],
) -> None:
    repo = JobRepo()
    pool = JobWorkerPool(
        worker_count=1,
        queue_size=1,
        repo=repo,
        session_manager=test_session_maker,
    )
    scheduler = JobScheduler(
        repo=repo,
        session_manager=test_session_maker,
        pool=pool,
    )
    stale_started_at = datetime.now(UTC) - timedelta(
        minutes=ENVS.SCHEDULAR.PROCESSING_JOB_TIMEOUT_MINUTES + 1
    )
    fresh_started_at = datetime.now(UTC)
    result = {"unique_words": 1, "word_count": 1}
    stmt = (
        sa.insert(DBJob)
        .values(
            [
                {
                    DBJob.text: "stale processing job",
                    DBJob.status: JobStatus.PROCESSING,
                    DBJob.start_processing_at: stale_started_at,
                    DBJob.result: None,
                    DBJob.processing_error: None,
                },
                {
                    DBJob.text: "fresh processing job",
                    DBJob.status: JobStatus.PROCESSING,
                    DBJob.start_processing_at: fresh_started_at,
                    DBJob.result: None,
                    DBJob.processing_error: None,
                },
                {
                    DBJob.text: "completed stale job",
                    DBJob.status: JobStatus.COMPLETED,
                    DBJob.start_processing_at: stale_started_at,
                    DBJob.result: result,
                    DBJob.processing_error: None,
                },
                {
                    DBJob.text: "failed stale job",
                    DBJob.status: JobStatus.FAILED,
                    DBJob.start_processing_at: stale_started_at,
                    DBJob.result: None,
                    DBJob.processing_error: "failed already",
                },
            ]
        )
        .returning(DBJob.id)
    )
    async with test_session_maker.begin() as session:
        stale_id, fresh_id, completed_id, failed_id = list(
            (await session.scalars(stmt)).all()
        )

    await scheduler.reset_stale_processing_jobs()

    select_stmt = sa.select(DBJob).where(
        DBJob.id.in_([stale_id, fresh_id, completed_id, failed_id])
    )
    async with test_session_maker.begin() as session:
        jobs = {job.id: job for job in (await session.scalars(select_stmt)).all()}

    stale_job = jobs[stale_id]
    assert stale_job.status == JobStatus.PENDING
    assert stale_job.start_processing_at is None
    assert stale_job.processing_error is None

    fresh_job = jobs[fresh_id]
    assert fresh_job.status == JobStatus.PROCESSING
    assert fresh_job.start_processing_at is not None

    completed_job = jobs[completed_id]
    assert completed_job.status == JobStatus.COMPLETED
    assert completed_job.result == result

    failed_job = jobs[failed_id]
    assert failed_job.status == JobStatus.FAILED
    assert failed_job.processing_error == "failed already"
