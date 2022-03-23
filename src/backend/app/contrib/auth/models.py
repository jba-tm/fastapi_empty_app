import sqlalchemy as sa

from app.db.models import Base


class User(Base):
    email = sa.Column(sa.String(255), unique=True, index=True, nullable=False)
    hashed_password = sa.Column(sa.String(500), nullable=False)


class Email(Base):
    email = sa.Column(sa.String(255), unique=True, index=True, nullable=False)
    is_active = sa.Column(sa.Boolean, default=False)
