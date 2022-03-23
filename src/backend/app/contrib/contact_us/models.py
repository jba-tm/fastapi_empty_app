import sqlalchemy as sa

from app.db.models import Base


class Message(Base):
    fullname = sa.Column(sa.String(255), default='', nullable=False)
    company_name = sa.Column(sa.String(255), default='', nullable=True)
    email = sa.Column(sa.String(255), nullable=False)
    phone_number = sa.Column(sa.String(255), default='', nullable=True)
    title = sa.Column(sa.String(255), nullable=False)
    body = sa.Column(sa.Text(), default='', nullable=False)

    created_at = sa.Column(sa.DateTime(timezone=True), server_default=sa.func.now())
    updated_at = sa.Column(sa.DateTime(timezone=True), onupdate=sa.func.now(), )