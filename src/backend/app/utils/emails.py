import emails
import logging
import os
from pathlib import Path
from typing import Any, Dict, Optional, List, TYPE_CHECKING
from emails.template import JinjaTemplate
from starlette_i18n import gettext_lazy as _
from app.conf.config import settings
from app.utils.templating import templates
from app.contrib.auth.repository import email_repo
from app.contrib.config.repository import config_repo
from app.db.session import SessionLocal

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from app.contrib.contact_us.models import Message


def send_email(
        email_to: str,
        subject_template: str = "",
        html_template: str = "",
        environment: Dict[str, Any] = None,
        attachments: Optional[list] = None,
) -> None:
    assert settings.EMAILS_ENABLED, "no provided configuration for email variables"
    if environment is None:
        environment = {}
    message = emails.Message(
        subject=JinjaTemplate(subject_template, environment=templates.env),
        html=JinjaTemplate(html_template, environment=templates.env),
        mail_from=(settings.EMAILS_FROM_NAME, settings.EMAILS_FROM_EMAIL),
    )
    smtp_options = {"host": settings.SMTP_HOST, "port": settings.SMTP_PORT}

    if settings.SMTP_TLS:
        smtp_options["tls"] = True
    if settings.SMTP_USER:
        smtp_options["user"] = settings.SMTP_USER
    if settings.SMTP_PASSWORD:
        smtp_options["password"] = settings.SMTP_PASSWORD
    response = message.send(to=email_to, render=environment, smtp=smtp_options)
    logging.info(f"send email result: {response}")
    return response


def send_test_email(email_to: str) -> None:
    project_name = settings.PROJECT_NAME
    subject = f"{project_name} - Test email"
    with open(Path(settings.EMAIL_TEMPLATES_DIR) / "test_email.html") as f:
        template_str = f.read()
    return send_email(
        email_to=email_to,
        subject_template=subject,
        html_template=template_str,
        environment={"project_name": settings.PROJECT_NAME, "email": email_to},
    )


def send_contact_us_messages(message: "Message"):
    with open(Path(settings.EMAIL_TEMPLATES_DIR) / "contact_messages.html") as f:
        template_str = f.read()
    db = SessionLocal()
    config = config_repo.get_by_params(db, {})
    if not config:
        config = config_repo.create(db)
    subject = _("%(site_name)s - contact messages") % {'site_name': config.site_name}
    recipient_emails = email_repo.get_all(db, q={'is_active': True})
    for email_to in recipient_emails:
        return send_email(
            email_to=email_to.email,
            subject_template=subject,
            html_template=template_str,
            environment={"site_name": config.site_name, "message": message},
        )
