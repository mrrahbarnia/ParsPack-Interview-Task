import typing as T
from dataclasses import dataclass
from enum import StrEnum, auto


class ErrorCode(StrEnum):
    NOT_FOUND = auto()
    VALIDATION_ERROR = auto()
    ALREADY_EXIST = auto()
    INTERNAL_ERROR = auto()


@dataclass(frozen=True)
class Error:
    code: ErrorCode
    message: str
    details: dict[str, T.Any] | None = None

    @classmethod
    def already_exist(
        cls,
        entity: str,
        duplicated_field: str | None = None,
        duplicated_value: str | None = None,
    ) -> T.Self:
        return cls(
            code=ErrorCode.ALREADY_EXIST,
            message=f"{entity} with {duplicated_field} {duplicated_value} already exist",
            details={"field": duplicated_field, "value": duplicated_value},
        )

    @classmethod
    def validation_error(cls, message: str) -> T.Self:
        return cls(code=ErrorCode.VALIDATION_ERROR, message=message)

    @classmethod
    def not_found(cls, entity: str, field_name: str, field_value: T.Any) -> T.Self:
        return cls(
            code=ErrorCode.NOT_FOUND,
            message=f"{entity} with {field_name} {field_value} not found",
            details={"field": field_name, "value": field_value},
        )

    @classmethod
    def internal_error(cls, message: str) -> T.Self:
        return cls(code=ErrorCode.INTERNAL_ERROR, message=message)
