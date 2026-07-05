import typing as T
import logging

from fastapi import status

from . import http_exceptions as exc
from ..service import Error, ErrorCode

logger = logging.getLogger(__name__)

V = T.TypeVar("V")


def map_errors_to_http_exceptions(
    error: Error,
) -> exc.AppBaseException:
    if error.code == ErrorCode.NOT_FOUND:
        return exc.EntityNotFoundException(message=error.message, data=error.details)

    elif error.code == ErrorCode.ALREADY_EXIST:
        return exc.DuplicateEntityException(message=error.message, data=error.details)

    elif error.code == ErrorCode.VALIDATION_ERROR:
        return exc.BadRequestException(message=error.message, data=error.details)

    else:
        return exc.ServerError(message=error.message, data=error.details)


def handle_service_errors(result: V | Error) -> V:
    if isinstance(result, Error):
        exception = map_errors_to_http_exceptions(result)
        if exception.status_code >= status.HTTP_500_INTERNAL_SERVER_ERROR:
            logger.error(
                f"Application error: {exception.message}",
                exc_info=True,
            )

        raise exception

    else:
        return result
