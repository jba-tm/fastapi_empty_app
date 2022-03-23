from typing import Optional
from fastapi import APIRouter, Request, Form, Depends
from sqlalchemy.orm import Session
from starlette_i18n import gettext_lazy as _
from fastapi.responses import RedirectResponse, HTMLResponse
from starlette.authentication import BaseUser
from starlette.status import HTTP_303_SEE_OTHER, HTTP_302_FOUND

from app.conf.config import settings, cookies_settings
from app.contrib.auth.forms import LoginForm
from app.contrib.auth.repository import user_repo
from app.routers.dependency import get_db, get_current_user
from app.utils.security import lazy_jwt_settings
from app.utils.templating import templates, flash
from .models import User

router = APIRouter()


def sign_in_user(
        request: Request,
        user: User,
        next_url: Optional[str] = None
) -> RedirectResponse:
    payload = lazy_jwt_settings.JWT_PAYLOAD_HANDLER(
        {'user_id': user.id, },
    )

    jwt_token = lazy_jwt_settings.JWT_ENCODE_HANDLER(payload)
    if not next_url:
        next_url = request.url_for('frontend:product-list-page')
    flash(request, str(_('You are signed in')))
    response = RedirectResponse(url=next_url, status_code=HTTP_302_FOUND)

    response.set_cookie(
        cookies_settings.COOKIE_TOKEN_NAME,
        f'Bearer {jwt_token}',
        expires=cookies_settings.COOKIE_EXPIRE,
        path=cookies_settings.COOKIE_PATH,
        httponly=True,
    )
    return response


@router.post('/login/', response_class=RedirectResponse, name='login')
def login(
        request: Request,
        next_url: Optional[str] = settings.LOGIN_REDIRECT,
        db: Session = Depends(get_db),
        email: str = Form(...),
        password: str = Form(...),
        user_req: BaseUser = Depends(get_current_user),

):
    """

    :param request:
    :param next_url:
    :param db:
    :param email:
    :param password:
    :param user_req:
    :return:
    """
    if user_req.is_authenticated:
        return RedirectResponse(next_url, status_code=HTTP_303_SEE_OTHER)

    form = LoginForm(
        email=email,
        password=password
    )
    if form.validate():
        user = user_repo.authenticate(
            db=db, email=email, password=password
        )
        if not user:
            form.email.errors = [_('Incorrect email or password')]
            return templates.TemplateResponse(
                'dashboard/auth/login.html',
                context={
                    'request': request, 'title': _('Login'), 'form': form
                }
            )
        response = sign_in_user(
            request=request, user=user, next_url=next_url,
        )

        return response
    else:
        return templates.TemplateResponse(
            'dashboard/auth/login.html',
            context={
                'request': request, 'title': _('Login'), 'form': form
            }
        )


@router.get('/login/', response_class=HTMLResponse, name='login-page')
def login_page(
        request: Request,
        next_url: Optional[str] = settings.LOGIN_REDIRECT,
        user: BaseUser = Depends(get_current_user),
):
    """

    :param request:
    :param next_url:
    :param user:
    :return:
    """
    if user.is_authenticated:
        return RedirectResponse(next_url, status_code=HTTP_303_SEE_OTHER)
    form = LoginForm()
    return templates.TemplateResponse(
        'dashboard/auth/login.html',
        context={
            'request': request, 'title': _('Login'), 'form': form, 'next': next,
        }
    )


@router.get('/logout/', response_class=RedirectResponse, name='logout')
async def logout(
        request: Request,
        user: BaseUser = Depends(get_current_user),
) -> RedirectResponse:
    """

    :param request:
    :param user:
    :return:
    """
    if not user.is_authenticated:
        return RedirectResponse(settings.LOGOUT_REDIRECT, status_code=HTTP_303_SEE_OTHER)
    response = RedirectResponse(url=settings.LOGOUT_REDIRECT, status_code=HTTP_303_SEE_OTHER)
    response.delete_cookie(cookies_settings.COOKIE_TOKEN_NAME, path=cookies_settings.COOKIE_PATH)
    flash(request, str(_('Your are logged out')))
    return response
