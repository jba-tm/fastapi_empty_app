from typing import Union, Optional
from uuid import UUID

from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenPayload(BaseModel):
    user_id: Union[int, UUID]
    iat: Optional[int] = None
    exp: int
