from wtforms import (StringField, EmailField, validators, PasswordField, BooleanField, IntegerField)

from wtforms_alchemy import ModelForm, PhoneNumberField
from starlette_i18n import gettext_lazy as _

from app.contrib.config.models import Config
from app.core.forms import check_phone_number, Unique
from app.contrib.auth.models import User, Email
from app.db.session import SessionLocal


class UserForm(ModelForm):
    email = EmailField(_('Email'), validators=[validators.DataRequired(),
                                               Unique(User.email, get_session=lambda: SessionLocal()),])
    password = PasswordField(_('Password'), validators=[validators.DataRequired()])

    class Meta:
        model = User
        only = 'email',


class UserUpdateForm(UserForm):
    password = PasswordField(_('Password'), )


class EmailForm(ModelForm):
    is_active = BooleanField(_('Is active'), )
    email = EmailField(_('Email'), validators=[validators.DataRequired()])

    class Meta:
        model = Email
        only = 'email', 'is_active'


class ConfigForm(ModelForm):
    site_name = StringField(_('Site name'), )
    seo_description = StringField(_('Seo description'), )
    company_name = StringField(_('Company name'), )
    address = StringField(_('Address'), )

    email = EmailField(_('Email'), )

    phone_number = PhoneNumberField(_('Phone number'), validators=[check_phone_number],
                                    display_format='international', )

    counter_line_value_1 = IntegerField(_('Counter line value 1'), )
    counter_line_name_1 = StringField(_('Counter line name 1'), )

    counter_line_value_2 = IntegerField(_('Counter line value 2'), )
    counter_line_name_2 = StringField(_('Counter line name 2'), )

    counter_line_value_3 = IntegerField(_('Counter line value 3'), )
    counter_line_name_3 = StringField(_('Counter line name 3'), )

    counter_line_value_4 = IntegerField(_('Counter line value 4'), )
    counter_line_name_4 = StringField(_('Counter line name 4'), )

    class Meta:
        model = Config
        only = (
            'company_name', 'site_name', 'email', 'phone_number', 'address', 'location',
            'counter_line_value_1', 'counter_line_name_1',
            'counter_line_value_2', 'counter_line_name_2',
            'counter_line_value_3', 'counter_line_name_3',
            'counter_line_value_4', 'counter_line_name_4',
        )
