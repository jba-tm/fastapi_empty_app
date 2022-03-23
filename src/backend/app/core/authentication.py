
from fastapi.exceptions import HTTPException

from pydantic import ValidationError
from starlette.status import HTTP_401_UNAUTHORIZED
from jose import jwt
from starlette.authentication import (
    AuthenticationBackend, BaseUser,
    AuthCredentials
)
from starlette_i18n import gettext_lazy as _

from fastapi.security.utils import get_authorization_scheme_param
from app.utils.security import lazy_jwt_settings
from app.conf.config import cookies_settings
from app.db.session import SessionLocal
from app.contrib.auth.repository import user_repo
from app.contrib.auth.schema import TokenPayload


class SimpleUser(BaseUser):
    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

    @property
    def is_authenticated(self) -> bool:
        return True

    @property
    def display_name(self) -> str:
        return self.user.fullname or _('Empty fullname')

    @property
    def fullname(self) -> str:
        return self.user.fullname

    @property
    def identity(self) -> str:
        raise NotImplementedError()  # pragma: no cover


class AuthBackend(AuthenticationBackend):
    async def authenticate(self, request):
        header_authorization: str = request.headers.get("Authorization")
        cookie_authorization: str = request.cookies.get(cookies_settings.COOKIE_TOKEN_NAME)
        header_scheme, header_param = get_authorization_scheme_param(
            header_authorization
        )
        cookie_scheme, cookie_param = get_authorization_scheme_param(
            cookie_authorization
        )

        if header_scheme.lower() == "bearer":
            authorization = True
            scheme = header_scheme
            token = header_param

        elif cookie_scheme.lower() == "bearer":
            authorization = True
            scheme = cookie_scheme
            token = cookie_param
        else:
            authorization = False
            scheme = ''
        if authorization or scheme.lower() == "bearer":
            try:
                payload = lazy_jwt_settings.JWT_DECODE_HANDLER(token)
                token_data = TokenPayload(**payload)
            except (jwt.JWTError, ValidationError):
                raise HTTPException(
                    status_code=HTTP_401_UNAUTHORIZED,
                    detail=str(_('Could not validate credentials')),
                    headers={"WWW-Authenticate": "Bearer"},
                )
            db = SessionLocal()

            user = user_repo.get_by_params(db, params={'id': token_data.user_id})
            return AuthCredentials(["authenticated"]), SimpleUser(user)
        return None
