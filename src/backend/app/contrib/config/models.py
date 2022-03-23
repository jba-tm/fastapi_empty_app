import sqlalchemy as sa

from app.db.models import Base


class Config(Base):
    company_name = sa.Column(sa.String(length=255), default='', )
    site_name = sa.Column(sa.String(length=255),  default='', )
    seo_description = sa.Column(sa.String(length=255),  default='', )

    email = sa.Column(sa.String(255), default='', )

    phone_number = sa.Column(sa.String(255), default='', )

    address = sa.Column(sa.String(length=255),  default='')
    location = sa.Column(sa.String(length=255),  default='')

    counter_line_value_1 = sa.Column(sa.Integer, default=0, )
    counter_line_name_1 = sa.Column(sa.String, default='', nullable=True)
    counter_line_value_2 = sa.Column(sa.Integer, default=0, )
    counter_line_name_2 = sa.Column(sa.String, default='', nullable=True)
    counter_line_value_3 = sa.Column(sa.Integer, default=0, )
    counter_line_name_3 = sa.Column(sa.String, default='', nullable=True)
    counter_line_value_4 = sa.Column(sa.Integer, default=0, )
    counter_line_name_4 = sa.Column(sa.String, default='', nullable=True)
