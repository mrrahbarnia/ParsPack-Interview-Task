import traceback
import logging
from typing import Annotated

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from fastapi import APIRouter, status, Depends

from . import dtos, dependencies as dc
from ....services import AuthService
from ....services.interfaces import IPasswordEncryptor, IAuthRepo

from src.shared.entrypoint import (
    # HTTPResponse,
    handle_service_errors,
    AppBaseException,
    ServerError,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth")


@router.post("/login", status_code=status.HTTP_200_OK)
async def login(
    payload: dtos.LoginRequest,
    session_maker: Annotated[
        async_sessionmaker[AsyncSession], Depends(dc.get_session_maker)
    ],
    password_encryptor: Annotated[
        IPasswordEncryptor, Depends(dc.get_password_encryptor)
    ],
    repo: Annotated[IAuthRepo, Depends(dc.get_repo)],
) -> str:
    #  -> HTTPResponse[dtos.LoginResponse]
    try:
        service_result = await AuthService(
            repo, password_encryptor, session_maker
        ).login(username=payload.username, password=payload.password)

        result = handle_service_errors(service_result)
        return result

    except AppBaseException:
        raise

    except Exception as ex:
        logger.error(traceback.format_exc())
        raise ServerError(data=str(ex))
