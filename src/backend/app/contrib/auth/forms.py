from wtforms import EmailField, Form, validators, PasswordField
from starlette_i18n import gettext_lazy as _


class LoginForm(Form):
    email = EmailField(_('Email'), validators=[validators.Length(min=6, max=100), validators.DataRequired()], )
    password = PasswordField(_('Password'), validators=[validators.Length(min=1, max=100), validators.DataRequired()], )