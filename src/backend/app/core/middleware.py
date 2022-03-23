import logging

from starlette_i18n import i18n, middleware
from starlette.middleware.authentication import AuthenticationMiddleware as BaseAuthenticationMiddleware
from dataclasses import dataclass, field

from starlette.middleware.base import RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response
from app.conf.config import settings

logger = logging.getLogger(__name__)


@dataclass
class LocaleFromQueryParamsMiddleware(middleware.BaseLocaleMiddleware):
    async def dispatch(
            self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        logger.debug("LocaleFromQueryParamsMiddleware::dispatch")

        locale_code = request.query_params.get('lang', settings.LANGUAGE_CODE)
        if locale_code:
            logger.debug(f"LocaleFromCookieMiddleware: set locale to: {locale_code}")
            i18n.set_locale(code=locale_code)
        request.LANGUAGE_CODE = locale_code
        response = await call_next(request)
        return response


class AuthenticationMiddleware(BaseAuthenticationMiddleware):
    pass
