import traceback
import logging
from typing import Annotated

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from fastapi import APIRouter, status, Depends

from . import dtos, dependencies as dc
from ....infra import JobRepo
from ....services import JobService
from ....types import JobID

from src.shared.const import DomainError
from src.modules.auth.types import UserID
from src.shared.entrypoint.dependencies import get_authenticated_user_id
from src.shared.entrypoint import (
    HTTPResponse,
    handle_service_errors,
    AppBaseException,
    ServerError,
    BadRequestException,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/jobs")


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_job(
    payload: dtos.JobCreateRequest,
    session_maker: Annotated[
        async_sessionmaker[AsyncSession], Depends(dc.get_session_maker)
    ],
    repo: Annotated[JobRepo, Depends(dc.get_repo)],
    _: Annotated[UserID, Depends(get_authenticated_user_id)],
) -> HTTPResponse[dtos.JobCreateResponse]:
    try:
        service_result = await JobService(repo, session_maker).create(text=payload.text)

        job_id = handle_service_errors(service_result)

        return HTTPResponse[dtos.JobCreateResponse](
            success=True,
            message="Logged in successfully.",
            data=dtos.JobCreateResponse(job_id=job_id),
        )

    except AppBaseException:
        raise

    except Exception as ex:
        logger.error(traceback.format_exc())
        raise ServerError(data=str(ex))


@router.get("/{job_id}", status_code=status.HTTP_200_OK)
async def get_job(
    job_id: JobID,
    session_maker: Annotated[
        async_sessionmaker[AsyncSession], Depends(dc.get_session_maker)
    ],
    repo: Annotated[JobRepo, Depends(dc.get_repo)],
    _: Annotated[UserID, Depends(get_authenticated_user_id)],
) -> HTTPResponse[dtos.JobDetailResponse]:
    try:
        service_result = await JobService(repo, session_maker).get_job_by_id(job_id)

        job = handle_service_errors(service_result)

        return HTTPResponse[dtos.JobDetailResponse](
            success=True,
            message="Logged in successfully.",
            data=dtos.JobDetailResponse(status=job.status, result=job.result),
        )

    except AppBaseException:
        raise

    except DomainError as ex:
        raise BadRequestException(data=None, message=ex.message)

    except Exception as ex:
        logger.error(traceback.format_exc())
        raise ServerError(data=str(ex))
