from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from src.shared.entrypoint import AppBaseException
from src.shared.entrypoint.dependencies import InvalidToken


async def unauthorized_exception_handler(
    request: Request,
    exc: InvalidToken,
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={
            "success": False,
            "message": "Unauthorized.",
            "data": {"reason": exc.__class__.__name__},
        },
    )


async def app_base_exception_handler(
    request: Request, exc: AppBaseException
) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": exc.success,
            "message": exc.message,
            "data": exc.data,
        },
    )


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(AppBaseException, app_base_exception_handler)  # type: ignore

    app.add_exception_handler(InvalidToken, unauthorized_exception_handler)  # type: ignore
