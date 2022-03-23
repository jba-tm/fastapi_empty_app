import os
import json

from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from fastapi.encoders import jsonable_encoder
from fastapi import Request
from datetime import datetime, timedelta
from typing import Optional

from fastapi.security.utils import get_authorization_scheme_param
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from fastapi.security import OAuth2, OAuth2PasswordRequestForm
from jose import jwt
from passlib.context import CryptContext
from starlette.status import HTTP_403_FORBIDDEN
from fastapi.exceptions import HTTPException
from app.conf.config import settings, jwt_settings, structure_settings
from .import_utils import perform_import

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

__all__ = ('get_token', 'jwt_payload', 'jwt_encode', 'jwt_decode', 'verify_password', 'get_password_hash',
           'generate_rsa_certificate', 'lazy_jwt_settings')

IMPORT_STRINGS = (
    'JWT_PASSWORD_VERIFY',
    'JWT_PASSWORD_HANDLER',
    'JWT_ENCODE_HANDLER',
    'JWT_DECODE_HANDLER',
    'JWT_PAYLOAD_HANDLER',
    'JWT_PAYLOAD_GET_USERNAME_HANDLER',
    'JWT_GET_USER_BY_NATURAL_KEY_HANDLER',
    'JWT_REFRESH_EXPIRED_HANDLER',
    'JWT_GET_REFRESH_TOKEN_HANDLER',
    'JWT_ALLOW_ANY_HANDLER',
    'JWT_ALLOW_ANY_CLASSES',
)


def get_token(user, context=None, **extra):
    payload = jwt_settings.JWT_PAYLOAD_HANDLER(user, context)
    payload.update(extra, )
    return jwt_settings.JWT_ENCODE_HANDLER(payload, context)


def jwt_payload(data: dict, expires_delta: Optional[timedelta] = None) -> dict:
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + jwt_settings.JWT_EXPIRATION_DELTA
    payload = data.copy()
    payload.update({"exp": int(round(expire.timestamp() * 1000))})
    return payload


def jwt_encode(payload, context=None) -> str:
    return jwt.encode(
        jsonable_encoder(payload),
        jwt_settings.JWT_PRIVATE_KEY or jwt_settings.JWT_SECRET_KEY,
        jwt_settings.JWT_ALGORITHM,
    )


def jwt_decode(token, context=None) -> dict:
    return jwt.decode(
        token=token,
        key=jwt_settings.JWT_PUBLIC_KEY or jwt_settings.JWT_SECRET_KEY,
        algorithms=[jwt_settings.JWT_ALGORITHM],
        options={
            'verify_signature': jwt_settings.JWT_VERIFY,
            'verify_exp': jwt_settings.JWT_VERIFY_EXPIRATION,
            'leeway': jwt_settings.JWT_LEEWAY,
        },
        audience=jwt_settings.JWT_AUDIENCE,
        issuer=jwt_settings.JWT_ISSUER,
    )


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def generate_rsa_certificate():
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )

    private_key_str = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )

    public_key = private_key.public_key()

    public_key_str = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )

    secrets: dict = {
        'private_key': private_key_str.decode("utf-8"),
        'public_key': public_key_str.decode("utf-8")
    }

    path = os.path.join(structure_settings.PROJECT_DIR, 'conf', 'secrets.json')

    with open(path, 'w') as f:
        f.write(json.dumps(secrets, sort_keys=True))

    return secrets


class JWTSettings:

    def __init__(self, defaults, import_strings):
        self.defaults = defaults
        self.import_strings = import_strings
        self._cached_attrs = set()

    def __getattr__(self, attr):
        if attr not in self.defaults:
            raise AttributeError('Invalid setting: `{}`'.format(attr))

        value = self.defaults.get(attr, self.defaults[attr])

        if attr in self.import_strings:
            value = perform_import(value, attr)

        self._cached_attrs.add(attr)
        setattr(self, attr, value)
        return value

    @property
    def user_settings(self):
        return self._user_settings

    def reload(self):
        for attr in self._cached_attrs:
            delattr(self, attr)

        self._cached_attrs.clear()

        if hasattr(self, '_user_settings'):
            delattr(self, '_user_settings')


lazy_jwt_settings = JWTSettings(jwt_settings.dict(), IMPORT_STRINGS)


class OAuth2PasswordBearerCookie(OAuth2):
    def __init__(
            self,
            tokenUrl: str,
            scheme_name: str = None,
            scopes: dict = None,
            auto_error: bool = True,
    ):
        if not scopes:
            scopes = {}
        flows = OAuthFlowsModel(password={"tokenUrl": tokenUrl, "scopes": scopes})
        super().__init__(flows=flows, scheme_name=scheme_name, auto_error=auto_error)

    async def __call__(self, request: Request) -> Optional[str]:
        header_authorization: str = request.headers.get("Authorization")
        cookie_authorization: str = request.cookies.get("Authorization")

        header_scheme, header_param = get_authorization_scheme_param(
            header_authorization
        )
        cookie_scheme, cookie_param = get_authorization_scheme_param(
            cookie_authorization
        )

        if header_scheme.lower() == "bearer":
            authorization = True
            scheme = header_scheme
            param = header_param

        elif cookie_scheme.lower() == "bearer":
            authorization = True
            scheme = cookie_scheme
            param = cookie_param

        else:
            authorization = False

        if not authorization or scheme.lower() != "bearer":
            if self.auto_error:
                raise HTTPException(
                    status_code=HTTP_403_FORBIDDEN, detail="Not authenticated"
                )
            else:
                return None
        return param
