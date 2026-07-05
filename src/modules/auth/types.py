from typing import NewType, TypedDict
from uuid import UUID

UserID = NewType("UserID", UUID)


class TokenPayload(TypedDict):
    user_id: UserID
