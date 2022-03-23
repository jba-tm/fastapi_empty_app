import uvicorn

from fastapi import FastAPI, Request
from fastapi.responses import  RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from starlette.status import HTTP_303_SEE_OTHER
from starlette_i18n import load_gettext_translations
from starlette.middleware import Middleware


from app.core.authentication import AuthBackend
from app.core.exceptions import UnAuthenticated
from app.core.middleware import AuthenticationMiddleware, LocaleFromQueryParamsMiddleware
from app.conf.config import settings, jwt_settings
from app.routers.urls import router
from app.sitemap import sitemap


def get_application() -> FastAPI:
    load_gettext_translations(directory=settings.LOCALE.get('DIR', 'locale'), domain='messages')
    application = FastAPI(
        default_response_class=ORJSONResponse,
        title=settings.PROJECT_NAME,
        debug=settings.DEBUG,
        version=settings.VERSION,
        middleware=[

            Middleware(LocaleFromQueryParamsMiddleware, default_code=settings.LANGUAGE_CODE),
            Middleware(SessionMiddleware, secret_key=jwt_settings.JWT_SECRET_KEY, ),
            Middleware(AuthenticationMiddleware, backend=AuthBackend()),
        ]
    )

    # Set all CORS enabled origins
    if settings.BACKEND_CORS_ORIGINS:
        application.add_middleware(
            CORSMiddleware,
            allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    application.mount("/static", StaticFiles(directory="static", html=True), name="static")
    application.include_router(router, )

    @application.exception_handler(UnAuthenticated)
    async def unauthenticated_template_exception_handler(request: Request, exc: UnAuthenticated):
        return RedirectResponse(settings.LOGIN_URL, status_code=HTTP_303_SEE_OTHER)

    application.add_route(
        path='/admin', route=RedirectResponse('/admin/user/')
    )

    application.add_route(
        path='/sitemap.xml', route=sitemap,
    )
    return application


app = get_application()

if __name__ == "__main__":
    uvicorn.run(get_application(), host="0.0.0.0", port=8000)
