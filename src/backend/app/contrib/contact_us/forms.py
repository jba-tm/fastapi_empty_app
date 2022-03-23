from wtforms import (Form, EmailField, validators, StringField, TextAreaField)
from starlette_i18n import gettext_lazy as _
from wtforms_alchemy import PhoneNumberField

from app.core.forms import check_phone_number


class ContactUsForm(Form):
    fullname = StringField(_('Fullname'), validators=[validators.DataRequired(), ], )
    company_name = StringField(_('Company name'), )
    title = StringField(_('Title'), validators=[validators.DataRequired(), ], )
    body = TextAreaField(_('Body'), validators=[validators.DataRequired(), ], )

    email = EmailField(
        _('Email'),
        validators=[validators.Length(min=6, max=100), validators.DataRequired(), ],
    )

    phone_number = PhoneNumberField(_('Phone number'), validators=[check_phone_number],
                                    display_format='international', )
