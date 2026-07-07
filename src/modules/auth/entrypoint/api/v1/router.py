import traceback
import logging
from typing import Annotated

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from fastapi import APIRouter, status, Depends

from . import dtos, dependencies as dc
from ....services import AuthService, IAuthRepo, IPasswordEncryptor
from ....infra import JWTService
from ....types import TokenPayload

from src.core.config import ENVS
from src.shared.entrypoint import (
    HTTPResponse,
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
    jwt_service: Annotated[JWTService, Depends(dc.get_jwt_service)],
    repo: Annotated[IAuthRepo, Depends(dc.get_repo)],
) -> HTTPResponse[dtos.LoginResponse]:
    try:
        service_result = await AuthService(
            repo, password_encryptor, session_maker
        ).login(username=payload.username, password=payload.password)

        result = handle_service_errors(service_result)

        access_token = jwt_service.create_access_token(
            token_payload=TokenPayload(user_id=result),
            access_token_expires_minute=ENVS.JWT.ACCESS_TOKEN_EXPIRES_MINUTE,
        )
        return HTTPResponse[dtos.LoginResponse](
            success=True,
            message="Logged in successfully.",
            data=dtos.LoginResponse(access_token=access_token, token_type="bearer"),
        )

    except AppBaseException:
        raise

    except Exception as ex:
        logger.error(traceback.format_exc())
        raise ServerError(data=str(ex))
