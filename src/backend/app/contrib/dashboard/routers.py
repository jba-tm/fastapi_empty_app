from typing import Optional, Union

from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import RedirectResponse, HTMLResponse
from starlette.datastructures import FormData
from starlette_i18n import gettext_lazy as _
from sqlalchemy.orm import Session
from starlette.status import HTTP_302_FOUND

from app.contrib.config.repository import config_repo
from app.contrib.contact_us.repository import message_repo
from app.contrib.dashboard.forms import ConfigForm, UserForm, UserUpdateForm, EmailForm
from app.routers.dependency import get_db, get_authenticated_user, get_commons
from app.contrib.auth.models import User
from app.utils.templating import templates, flash
from app.conf.config import settings
from app.contrib.auth.repository import user_repo, email_repo

router = APIRouter()


@router.get('/user/', response_class=HTMLResponse, name='user-list-page')
def get_users(
        request: Request,
        commons: Optional[dict] = Depends(get_commons),
        user: User = Depends(get_authenticated_user),
        db: Session = Depends(get_db),
) -> HTMLResponse:
    limit = commons.get('limit', settings.PAGINATION_MAX_SIZE)
    offset = commons.get('offset', 0)
    q = commons.get('q')

    object_list = user_repo.get_all(db=db, q=q, limit=limit, offset=offset)
    total = user_repo.count(db, q=q)
    return templates.TemplateResponse(
        'dashboard/auth/user/list_view.html',
        {
            'request': request,
            'title': _('Users'),
            'limit': limit,
            'page': commons.get('page', 1),
            'total': total,
            'object_list': object_list,
        }
    )


@router.get('/user/create/', response_class=HTMLResponse, name='user-create-page')
def user_create_page(
        request: Request,
        user: User = Depends(get_authenticated_user),
) -> HTMLResponse:
    form = UserForm()
    return templates.TemplateResponse(
        'dashboard/auth/user/create_view.html',
        {
            'request': request,
            'form': form,
            'title': _('Create user')
        }
    )


@router.post('/user/create/', response_class=RedirectResponse, name='user-create')
def create_user(
        request: Request,
        email: str = Form(...),
        password: str = Form(...),

        user: User = Depends(get_authenticated_user),
        db: Session = Depends(get_db),
) -> Union[HTMLResponse, RedirectResponse]:
    data = {
        'email': email,
        'password': password,
    }
    form = UserForm(data=data)
    if form.validate():
        user = user_repo.create(db=db, obj_in=data)
        flash(request, str(_('User successfully created')), )
        return RedirectResponse(request.url_for('user-update-page', email_in=user.email), status_code=HTTP_302_FOUND)
    return templates.TemplateResponse(
        'dashboard/auth/user/create_view.html',
        {
            'request': request,
            'form': form,
            'title': _('Create user')
        }
    )


@router.get('/user/{email_in}/detail/', response_class=HTMLResponse, name='user-detail-page')
def get_single_user(
        request: Request,
        email_in: str,

        user: User = Depends(get_authenticated_user),
        db: Session = Depends(get_db),
) -> Union[HTMLResponse, RedirectResponse]:
    user_in = user_repo.get_by_email(db, email=email_in)
    if not user_in:
        flash(request, str(_("User does not exist")), 'warning')
        return RedirectResponse(request.url_for('user-detail-page', email_in=user_in.email), status_code=HTTP_302_FOUND)

    return templates.TemplateResponse(
        'dashboard/auth/user/detail_view.html',
        {
            'request': request,
            'object': user_in,
            'title': _("User: %(model)s") % {'model': user_in.email}
        }
    )


@router.get('/user/{email_in}/update/', response_class=HTMLResponse, name='user-update-page')
def user_update_page(
        request: Request,
        email_in: str,
        user: User = Depends(get_authenticated_user),
        db: Session = Depends(get_db),
) -> Union[HTMLResponse, RedirectResponse]:
    user_in = user_repo.get_by_email(db, email=email_in)
    if not user_in:
        flash(request, str(_("User does not exist")), 'warning')
        return RedirectResponse(request.url_for('user-list-page', ), status_code=HTTP_302_FOUND)
    form = UserUpdateForm(obj=user)
    return templates.TemplateResponse(
        'dashboard/auth/user/update_view.html',
        {
            'request': request,
            'form': form,
            'title': _('Edit user: %(model)s') % {'model': user.email}
        }
    )


@router.post('/user/{email_in}/update/', response_class=RedirectResponse, name='user-update')
def update_user(
        request: Request,
        email_in: str,
        email: str = Form(...),
        password: Optional[str] = Form(None),
        user: User = Depends(get_authenticated_user),
        db: Session = Depends(get_db),
) -> Union[RedirectResponse, HTMLResponse]:
    user_in = user_repo.get_by_email(db, email=email_in)
    if not user_in:
        flash(request, str(_("User does not exist")), 'warning')
        return RedirectResponse(request.url_for('user-list-page', ), status_code=HTTP_302_FOUND)
    data = {
        'email': email,
        'password': password,
    }
    form_data = FormData(**data)
    form = UserUpdateForm(obj=user_in, formdata=form_data)
    if form.validate():
        user_repo.update(db=db, db_obj=user_in, obj_in=data)
        flash(request, str(_('User successfully updated')))
        return RedirectResponse(request.url_for('user-detail-page', email_in=user_in.email), status_code=HTTP_302_FOUND)

    return templates.TemplateResponse(
        'dashboard/auth/user/update_view.html',
        {
            'request': request,
            'form': form,
            'title': _('Edit user: %(model)s') % {'model': user.email}
        }
    )


@router.get('/user/{email_in}/delete/', response_class=RedirectResponse, name='user-delete')
def delete_user(
        request: Request,
        email_in: str,
        user: User = Depends(get_authenticated_user),
        db: Session = Depends(get_db),
) -> RedirectResponse:
    user_in = user_repo.get_by_email(db, email=email_in)
    response = RedirectResponse(request.url_for('user-list-page', ), status_code=HTTP_302_FOUND)
    if not user_in:
        flash(request, str(_("User does not exist")), 'warning')
        return response
    if user_in.email == user.email:
        flash(request, str(_("You can't delete yourself")), 'warning')
    else:
        flash(request, str(_('User successfully deleted')))
        user_repo.delete(db, db_obj=user_in)
    return response


@router.get('/email/', response_class=HTMLResponse, name='email-list-page')
def get_emails(

        request: Request,
        commons: Optional[dict] = Depends(get_commons),
        user: User = Depends(get_authenticated_user),
        db: Session = Depends(get_db),
) -> HTMLResponse:
    limit = commons.get('limit', settings.PAGINATION_MAX_SIZE)
    offset = commons.get('offset', 0)
    q = commons.get('q')

    object_list = email_repo.get_all(db=db, q=q, limit=limit, offset=offset)
    total = message_repo.count(db, q=q)

    return templates.TemplateResponse(
        'dashboard/auth/email/list_view.html',
        {
            'request': request,
            'title': _('Emails'),
            'limit': limit,
            'page': commons.get('page', 1),
            'total': total,
            'object_list': object_list,
        }
    )


@router.get('/email/create/', response_class=HTMLResponse, name='email-create-page')
def create_email_page(
        request: Request,
        user: User = Depends(get_authenticated_user),
) -> HTMLResponse:
    form = EmailForm()
    return templates.TemplateResponse(
        'dashboard/auth/email/create_view.html',
        {
            'request': request,
            'form': form,
            'title': _('Add email'),
        }
    )


@router.post('/email/create/', response_class=RedirectResponse, name='email-create')
def create_email(
        request: Request,
        email: str = Form(...),
        is_active: Optional[bool] = Form(False),
        user: User = Depends(get_authenticated_user),
        db: Session = Depends(get_db),
) -> Union[HTMLResponse, RedirectResponse]:
    data = {
        'email': email,
        "is_active": is_active
    }
    form = EmailForm(data=data)
    if form.validate():
        obj = email_repo.create(db=db, obj_in=data)
        flash(request, str(_('Email successfully created')))
        return RedirectResponse(request.url_for('email-detail-page', email_in=obj.email), status_code=HTTP_302_FOUND)

    return templates.TemplateResponse(
        'dashboard/auth/email/create_view.html',
        {
            'request': request,
            'form': form,
            'title': _('Add email')
        }
    )


@router.get('/email/{email_in}/detail/', response_class=HTMLResponse, name='email-detail-page')
def get_single_email(
        request: Request,
        email_in: str,
        user: User = Depends(get_authenticated_user),
        db: Session = Depends(get_db),
) -> Union[HTMLResponse, RedirectResponse]:
    obj = email_repo.get_by_params(db=db, params={'email': email_in})
    if not obj:
        flash(request, str(_("Email does not exist")), 'warning')
        return RedirectResponse(request.url_for('email-list-page', ), status_code=HTTP_302_FOUND)
    return templates.TemplateResponse(
        'dashboard/auth/email/detail_view.html',
        {
            'title': _('Email: %(model)s') % {'model': obj.email},
            'request': request,
            'object': obj,
        }
    )


@router.get('/email/{email_in}/update/', response_class=HTMLResponse, name='email-update-page')
def update_email_page(

        request: Request,
        email_in: str,
        user: User = Depends(get_authenticated_user),
        db: Session = Depends(get_db),
) -> Union[RedirectResponse, HTMLResponse]:
    obj = email_repo.get_by_params(db=db, params={'email': email_in})
    if not obj:
        flash(request, str(_("Email does not exist")), 'warning')
        return RedirectResponse(request.url_for('email-detail-page', email_in=obj.email), status_code=HTTP_302_FOUND)
    form = EmailForm(obj=obj)

    return templates.TemplateResponse(
        'dashboard/auth/email/update_view.html',
        {
            'request': request,
            'title': _('Update email: %(model)s') % {'model': obj.email},
            'form': form,
        }
    )


@router.post('/email/{email_in}/update/', response_class=RedirectResponse, name='email-update')
def update_email(
        request: Request,
        email_in: str,
        email: str = Form(...),
        is_active: Optional[bool] = Form(False),
        db: Session = Depends(get_db),
        user: User = Depends(get_authenticated_user)
) -> Union[HTMLResponse, RedirectResponse]:
    obj = email_repo.get_by_params(db=db, params={'email': email_in})
    if not obj:
        flash(request, str(_("Email does not exist")), 'warning')
        return RedirectResponse(request.url_for('email-list-page', ), status_code=HTTP_302_FOUND)
    data = {
        'email': email,
        'is_active': is_active
    }
    form_data = FormData(**data)
    form = EmailForm(obj=obj, formdata=form_data)
    if form.validate():
        obj = email_repo.update(db=db, db_obj=obj, obj_in=data)
        flash(request, str(_('Email successfully updated')))
        return RedirectResponse(request.url_for('email-update-page', email_in=obj.email), status_code=HTTP_302_FOUND)

    return templates.TemplateResponse(
        'dashboard/auth/email/update_view.html',
        {
            'request': request,
            'title': _('Update email: %(model)s') % {'model': obj.email},
            'form': form,
        }
    )


@router.get('/email/{email_in}/delete/', response_class=RedirectResponse, name='email-delete')
def delete_email(
        request: Request,
        email_in: str,
        user: User = Depends(get_authenticated_user),
        db: Session = Depends(get_db),
) -> RedirectResponse:
    obj = email_repo.get_by_params(db, params={'email': email_in})
    response = RedirectResponse(request.url_for('email-list-page', ), status_code=HTTP_302_FOUND)
    if not obj:
        flash(request, str(_("Email does not exist")), 'warning')
        return response
    else:
        flash(request, str(_('Email successfully deleted')))
        user_repo.delete(db, db_obj=obj)
    return response


@router.get('/message/', response_class=HTMLResponse, name='message-list-page')
def get_messages(
        request: Request,
        commons: Optional[dict] = Depends(get_commons),
        user: User = Depends(get_authenticated_user),
        db: Session = Depends(get_db),
) -> HTMLResponse:
    limit = commons.get('limit', settings.PAGINATION_MAX_SIZE)
    offset = commons.get('offset', 0)
    q = commons.get('q')

    object_list = message_repo.get_all(db=db, q=q, limit=limit, offset=offset,
                                       order_by=(message_repo.model.created_at.desc(),))
    total = message_repo.count(db, q=q)

    return templates.TemplateResponse(
        'dashboard/message/list_view.html',
        {
            'request': request,
            'title': _('Messages'),
            'limit': limit,
            'page': commons.get('page', 1),
            'total': total,
            'object_list': object_list,
        }
    )


@router.get('/message/{obj_id}/detail/', response_class=HTMLResponse, name='message-detail-page')
def get_message(
        request: Request,
        obj_id: str,
        user: User = Depends(get_authenticated_user),
        db: Session = Depends(get_db),
) -> Union[HTMLResponse, RedirectResponse]:
    message = message_repo.get_by_params(db=db, params={'id': obj_id})
    if not message:
        flash(request, str(_('Message does not exist')), 'warning')
        return RedirectResponse(request.url_for('message-list-page'), status_code=HTTP_302_FOUND, )
    return templates.TemplateResponse(
        'dashboard/message/detail_view.html',
        {
            'request': request,
            'object': message,
            'title': _('Message: %(model)s') % {'model': message.title},
        }
    )


@router.get('/config/', response_class=HTMLResponse, name='config-detail-page')
def get_config(
        request: Request,
        user: User = Depends(get_authenticated_user),
        db: Session = Depends(get_db),
) -> HTMLResponse:
    config = config_repo.get_by_params(db=db, params={})
    if not config:
        flash(request, str(_('Config created')))
        config = config_repo.create(db, obj_in={})

    return templates.TemplateResponse(
        'dashboard/config/detail_view.html',
        {
            'request': request, 'title': _('Site configuration'), 'object': config,
            'object_actions': (
                {'url': request.url_for('config-update-page', ), 'name': _('Edit')},
            )
        }
    )


@router.get('/config/update/', response_class=HTMLResponse, name='config-update-page')
def config_update_page(
        request: Request,
        user: User = Depends(get_authenticated_user),
        db: Session = Depends(get_db),
) -> HTMLResponse:
    config = config_repo.get_by_params(db=db, params={})
    if not config:
        flash(request, str(_('Config created')), )
        config = config_repo.create(db, obj_in={})
    form = ConfigForm(obj=config)
    return templates.TemplateResponse(
        'dashboard/config/update_view.html',
        {
            'request': request,
            'form': form,
            'title': _('Update site configuration')
        }
    )


@router.post('/config/update/', response_class=RedirectResponse, name='config-update')
def update_config(
        request: Request,
        email: Optional[str] = Form(None),
        site_name: Optional[str] = Form(None),
        seo_description: Optional[str] = Form(None),
        address: Optional[str] = Form(None),
        location: Optional[str] = Form(None),
        company_name: Optional[str] = Form(None),
        phone_number: Optional[str] = Form(None),
        counter_line_value_1: Optional[str] = Form(None),
        counter_line_name_1: Optional[str] = Form(None),
        counter_line_value_2: Optional[str] = Form(None),
        counter_line_name_2: Optional[str] = Form(None),
        counter_line_value_3: Optional[str] = Form(None),
        counter_line_name_3: Optional[str] = Form(None),
        counter_line_value_4: Optional[str] = Form(None),
        counter_line_name_4: Optional[str] = Form(None),
        user: User = Depends(get_authenticated_user),
        db: Session = Depends(get_db),
) -> Union[HTMLResponse, RedirectResponse]:
    config = config_repo.get_by_params(db=db, params={})
    if not config:
        flash(request, str(_('Config created')))
        config = config_repo.create(db, obj_in={})
    data = {
        'email': email,
        'phone_number': phone_number,
        'site_name': site_name,
        'seo_description': seo_description,
        'company_name': company_name,
        'address': address,
        'location': location,
        'counter_line_value_1': counter_line_value_1,
        'counter_line_name_1': counter_line_name_1,
        'counter_line_value_2': counter_line_value_2,
        'counter_line_name_2': counter_line_name_2,
        'counter_line_value_3': counter_line_value_3,
        'counter_line_name_3': counter_line_name_3,
        'counter_line_value_4': counter_line_value_4,
        'counter_line_name_4': counter_line_name_4,
    }

    form_data = FormData(**data)

    form = ConfigForm(obj=config, formdata=form_data)
    if form.validate():
        config_repo.update(db=db, db_obj=config, obj_in=data)
        flash(request, str(_('Site configuration successfully updated')))
        return RedirectResponse(request.url_for('config-detail-page'), status_code=HTTP_302_FOUND)

    return templates.TemplateResponse(

        'dashboard/config/update_view.html',
        {
            'request': request,
            'form': form,
            'title': _('Update site configuration')
        }
    )
