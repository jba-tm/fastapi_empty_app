from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from app.utils.templating import templates
from app.routers.dependency import get_db
from app.contrib.contact_us.forms import ContactUsForm
from app.contrib.config.repository import config_repo

router = APIRouter()


@router.get('/', response_class=HTMLResponse, name='home-page')
async def home_page(request: Request, db: Session = Depends(get_db)):
    """
    Home page
    """
    config = config_repo.get_by_params(db, {})
    if not config:
        config = config_repo.create(db)

    form = ContactUsForm()
    return templates.TemplateResponse(
        'frontend/home/index.html',
        context={
            'request': request,
            'form': form,
            'config': config,
            'title': config.company_name,
            'seo_description': config.seo_description or config.site_name,
        },
    )
