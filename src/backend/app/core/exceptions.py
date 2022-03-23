from fastapi import status, HTTPException
from typing import Any, Optional, Dict

from starlette_i18n import gettext_lazy as _


class UnAuthenticated(HTTPException):
    def __init__(
            self,
            status_code: int = status.HTTP_401_UNAUTHORIZED,
            detail: Any = str(_('Un authenticated')),
            headers: Optional[Dict[str, Any]] = None,
    ) -> None:
        if headers is None:
            headers = {"WWW-Authenticate": "Bearer"}
        super().__init__(status_code=status_code, detail=detail, headers=headers)
