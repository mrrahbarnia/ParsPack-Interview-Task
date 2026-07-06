from typing import Annotated

from pydantic import AfterValidator


def strip_str(s: str) -> str:
    return s.strip()


StrippedStr = Annotated[str, AfterValidator(strip_str)]
