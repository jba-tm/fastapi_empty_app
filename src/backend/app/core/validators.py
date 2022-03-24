from wtforms_alchemy.validators import Unique as BaseUnique
from wtforms import ValidationError, validators

from starlette_i18n import gettext_lazy as _
from phonenumbers import (
    NumberParseException,
    PhoneNumberType,
    is_valid_number,
    number_type,
    parse as parse_phone_number, PhoneNumber,
)


# MOBILE_NUMBER_TYPES = PhoneNumberType.MOBILE, PhoneNumberType.FIXED_LINE_OR_MOBILE


class Unique(BaseUnique):
    def __call__(self, form, field):
        columns = self._syntaxes_as_tuples(form, field, self.column)
        self.model = columns[0][1].class_
        query = self.query
        if not hasattr(form, '_obj'):
            raise Exception(
                "Couldn't access Form._obj attribute. Either make your form "
                "inherit WTForms-Alchemy ModelForm or WTForms-Components "
                "ModelForm or make this attribute available in your form."
            )

        for field_name, column in columns:
            id_in = None
            if form._obj:
                id_in = getattr(form._obj, 'id')
            exist = self.get_session().query(query.filter(column == form[field_name].data,
                                                          self.model.id != id_in).exists()).scalar()
            if exist:
                if self.message is None:
                    self.message = field.gettext(u'Already exists.')
                raise ValidationError(self.message)


def check_phone_number(form, field):
    value = field.data
    if value is None:
        return value
    elif isinstance(value, PhoneNumber):
        value = value.international
    try:
        n = parse_phone_number(value, )
    except NumberParseException as e:
        raise ValidationError(_('Please provide a valid mobile phone number'))

    if not is_valid_number(n) or number_type(n) not in PhoneNumberType.values():
        raise ValidationError(_('Please provide a valid mobile phone number'))
    return n
    # return format_number(n, PhoneNumberFormat.NATIONAL if n.country_code == 44 else PhoneNumberFormat.INTERNATIONAL)


def validate_file_required(form, field, ):
    if not field.data.filename:
        raise validators.ValidationError(_('This field required'))

    else:
        content_type = field.data.content_type
        if content_type not in {'image/jpeg', 'image/png', 'application/pdf'}:
            raise validators.ValidationError(_('Image type must be: png, jpg or gif'))


def validate_file(self, field):
    file = field.data
    if field.data and file.filename != '':
        content_type = field.data.content_type
        if content_type not in {'image/jpeg', 'image/png', 'application/pdf'}:
            raise validators.ValidationError(_('Image type must be: png, jpg, svg or gif'))