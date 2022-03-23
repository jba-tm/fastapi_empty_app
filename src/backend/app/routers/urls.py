from fastapi import APIRouter
from fastapi.responses import FileResponse

from app.contrib.auth.routers import router as auth_router
from app.contrib.home.routers import router as home_router
from app.contrib.contact_us.routers import router as contact_router
from app.contrib.dashboard.routers import router as dashboard_router

router = APIRouter()

router.include_router(auth_router, tags=['home'], prefix='/auth')
router.include_router(dashboard_router, tags=['dashboard'], prefix='/admin')
router.include_router(home_router, tags=['home'], )
router.include_router(contact_router, tags=['contact_us'], )


@router.get('/favicon.ico', response_class=FileResponse, name='favicon')
async def favicon() -> str:
    return 'static/images/logo/favicon.ico'


# @router.get('/sitemap.xml', response_class=FileResponse, name='favicon')
# async def favicon() -> str:
#     return 'static/sitemap.xml'


@router.get('/robots.txt', response_class=FileResponse, name='robots')
async def favicon() -> str:
    return 'robots.txt'
