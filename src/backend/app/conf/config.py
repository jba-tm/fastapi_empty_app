import secrets
from typing import Any, Dict, List, Optional, Union
from pathlib import Path
from pydantic import AnyHttpUrl, BaseSettings, EmailStr, validator
from datetime import timedelta


class Settings(BaseSettings):
    # Dirs
    BASE_DIR: Optional[str] = Path(__file__).resolve().parent.parent.parent.as_posix()
    PROJECT_DIR: Optional[str] = Path(__file__).resolve().parent.parent.as_posix()
    # Project
    VERSION: Optional[str] = '0.1.0'
    DEBUG: Optional[bool] = False
    PAGINATION_MAX_SIZE: int = 25

    DOMAIN: Optional[str] = 'localhost:8000'
    SITE_URL: str = 'http://localhost'
    API_V1_STR: str = "/api/v1"
    # 60 minutes * 24 hours * 8 days = 8 days
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8

    SERVER_NAME: str
    SERVER_HOST: AnyHttpUrl
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    PROJECT_NAME: str

    @validator("EMAILS_FROM_NAME")
    def get_project_name(cls, v: Optional[str], values: Dict[str, Any]) -> str:
        if not v:
            return values["PROJECT_NAME"]
        return v

    SQLALCHEMY_DATABASE_URI: Optional[str] = 'sqlite:///sqlite.db'
    SMTP_TLS: Optional[bool] = True
    SMTP_PORT: Optional[int] = 587
    SMTP_HOST: Optional[str] = 'smtp.mail.ru'
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAILS_FROM_EMAIL: Optional[EmailStr] = None
    EMAILS_FROM_NAME: Optional[str] = None

    EMAIL_RESET_TOKEN_EXPIRE_HOURS: int = 48
    EMAIL_TEMPLATES_DIR: Optional[str] = "app/email-templates/build"
    EMAILS_ENABLED: Optional[bool] = True

    EMAIL_TEST_USER: EmailStr = "test@example.com"  # type: ignore
    FIRST_SUPERUSER: EmailStr
    FIRST_SUPERUSER_PASSWORD: str

    RECAPTCHA_SITE_KEY = '6Lea-JIeAAAAAAtNalh0-F6Wsze6-TCNJ4dl-D5y'
    RECAPTCHA_SECRET_KEY = '6Lea-JIeAAAAAO1EgOVuAIE_BWaT9PnkA4PJTPa1'

    DASHBOARD_PATH_PREFIX: str = '/admin'

    LOGIN_TEMPLATE: str = 'admin/auth/login.html'

    LOGIN_URL = '/auth/login/'
    LOGIN_REDIRECT = '/admin/user/'
    LOGOUT_REDIRECT = '/auth/login/'

    LANGUAGE_CODE: Optional[str] = 'ru'


    LOCALE: Dict[str, Any] = {
        'DIR': 'locale'
    }
    class Config:
        case_sensitive = True
        env_file = '.env'
        env_file_encoding = 'utf-8'


class JWTSettings(BaseSettings):
    # Security
    JWT_SECRET_KEY: str = secrets.token_urlsafe(32)
    # JWT
    JWT_PUBLIC_KEY: str = None
    JWT_PRIVATE_KEY: str = None
    JWT_ALGORITHM: str = "RS256"
    JWT_VERIFY: bool = True
    JWT_VERIFY_EXPIRATION: bool = True
    JWT_LEEWAY: int = 0
    JWT_ARGUMENT_NAME: str = 'token'
    # 60 minutes * 24 hours * 8 days = 8 days
    JWT_EXPIRATION_DELTA: timedelta = timedelta(minutes=5.0)
    JWT_ALLOW_REFRESH: str = True
    JWT_REFRESH_EXPIRATION_DELTA: timedelta = timedelta(days=7)
    JWT_AUTH_HEADER_NAME: str = 'HTTP_AUTHORIZATION'
    JWT_AUTH_HEADER_PREFIX: str = 'Bearer'
    # Helper functions
    JWT_PASSWORD_VERIFY: object = 'app.utils.security.verify_password'
    JWT_PASSWORD_HANDLER: object = 'app.utils.security.get_password_hash'
    JWT_PAYLOAD_HANDLER: object = 'app.utils.security.jwt_payload'
    JWT_ENCODE_HANDLER: object = 'app.utils.security.jwt_encode'
    JWT_DECODE_HANDLER: object = 'app.utils.security.jwt_decode'
    JWT_AUDIENCE: Any = None
    JWT_ISSUER: Any = None

    class Config:
        case_sensitive = True
        env_file = '.env'
        env_file_encoding = 'utf-8'


class StructureSettings(BaseSettings):
    # Dirs
    BASE_DIR: Optional[str] = Path(__file__).resolve().parent.parent.parent.as_posix()
    PROJECT_DIR: Optional[str] = Path(__file__).resolve().parent.parent.as_posix()
    MEDIA_DIR: str = 'media'  # Without end slash
    MEDIA_URL: str = '/media/'

    STATIC_DIR: str = 'static'
    STATIC_URL: str = '/static/'

    TEMPLATES: dict = {
        'DIR': 'templates'
    }

    TEMP_PATH: str = 'temp/'

    LOCALE: Dict[str, Any] = {
        'DIRS': [
            'app/locale',
            'locale'
        ],
    }

    class Config:
        case_sensitive = True
        env_file = '.env'
        env_file_encoding = 'utf-8'


class CookiesSettings(BaseSettings):
    COOKIE_REMEMBER_ME_EXPIRE: int = 3600 * 24 * 30
    COOKIE_EXPIRE: int = 60 * 60 * 24 * 30
    COOKIE_PATH: str = '/'
    COOKIE_TOKEN_NAME: str = 'Authorization'

    # redis cache
    CACHE_CAPTCHA_ID: str = "captcha:{captcha_id}"
    CACHE_LOGIN_ERROR_TIMES: str = "login_error_times:{ip}"
    CACHE_LOGIN_USER: str = "login_user:{token}"
    CHECKOUT_EXPIRE: int = 60 * 20


settings = Settings()
jwt_settings = JWTSettings()
structure_settings = StructureSettings()
cookies_settings = CookiesSettings()
