from wtforms import EmailField, Form, validators, PasswordField
from wtforms_alchemy import ModelForm
from starlette_i18n import gettext_lazy as _

from app.db.session import SessionLocal
from .models import User
from app.core.validators import Unique


class LoginForm(ModelForm):
    email = EmailField(_('Email'), validators=[validators.Length(min=6, max=100), validators.DataRequired(), ], )
    password = PasswordField(_('Password'), validators=[validators.Length(min=1, max=100), validators.DataRequired()], )

    class Meta:
        model = User
        only = 'email',
