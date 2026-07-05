from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from src.shared.entrypoint import AppBaseException


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
