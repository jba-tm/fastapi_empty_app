from typing import Optional, Union
from starlette.status import HTTP_302_FOUND
from fastapi import APIRouter, Depends, Request, Form, BackgroundTasks
from sqlalchemy.orm import Session
from fastapi.responses import HTMLResponse, RedirectResponse
from starlette_i18n import gettext_lazy as _
from app.utils.templating import templates, flash
from .forms import ContactUsForm
from .repository import message_repo
from app.routers.dependency import get_db
from app.utils.emails import send_contact_us_messages

router = APIRouter()


@router.post('/', response_class=RedirectResponse, name='contact-us')
def contact_us(
        request: Request,

        background_tasks: BackgroundTasks,
        fullname: str = Form(...),
        email: str = Form(...),
        title: str = Form(...),
        body: str = Form(...),
        company_name: Optional[str] = Form(None),
        phone_number: Optional[str] = Form(None),
        db: Session = Depends(get_db),
) -> Union[RedirectResponse, HTMLResponse]:
    data = {
        'fullname': fullname,
        'email': email,
        'title': title,
        'body': body,
        'company_name': company_name,
        'phone_number': phone_number
    }
    form = ContactUsForm(data=data)
    if form.validate():
        message = message_repo.create(db=db, obj_in=data)
        background_tasks.add_task(send_contact_us_messages, message, )
        flash(request, str(_('Message successfully sent')))
        return RedirectResponse(request.url_for('home-page'), status_code=HTTP_302_FOUND)
    return templates.TemplateResponse(
        'frontend/home/index.html',
        context={
            'request': request,
            'form': form,
        },
    )
