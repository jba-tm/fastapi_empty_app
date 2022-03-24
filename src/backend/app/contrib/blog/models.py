import sqlalchemy as sa

from app.db.models import Base


class Post(Base):
    slug = sa.Column(sa.String(length=255), unique=True)
    title = sa.Column(sa.String(length=255), )
    content = sa.Column(sa.Text(), default='')

    created_at = sa.Column(sa.DateTime(timezone=True), server_default=sa.func.now())
    updated_at = sa.Column(sa.DateTime(timezone=True), onupdate=sa.func.now(), )
