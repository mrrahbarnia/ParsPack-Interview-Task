import traceback
import logging
from typing import Annotated

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from fastapi import APIRouter, status, Depends

from . import dtos, dependencies as dc
from ....services import JobService, IJobRepo

from src.shared.entrypoint import (
    HTTPResponse,
    handle_service_errors,
    AppBaseException,
    ServerError,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/jobs")


@router.post("", status_code=status.HTTP_200_OK)
async def create_job(
    payload: dtos.JobCreateRequest,
    session_maker: Annotated[
        async_sessionmaker[AsyncSession], Depends(dc.get_session_maker)
    ],
    repo: Annotated[IJobRepo, Depends(dc.get_repo)],
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
