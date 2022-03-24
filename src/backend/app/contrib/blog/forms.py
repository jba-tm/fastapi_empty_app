from wtforms import (validators, StringField, TextAreaField)
from wtforms_alchemy import ModelForm
from starlette_i18n import gettext_lazy as _
from app.db.session import SessionLocal
from .models import Post
from app.core.validators import Unique


class PostForm(ModelForm):
    slug = StringField(_('Slug'), validators=[validators.DataRequired(),
                                              Unique(Post.slug, get_session=lambda: SessionLocal()), ], )
    title = StringField(_('Title'), validators=[validators.DataRequired(), ], )
    content = TextAreaField(_('Content'), )

    class Meta:
        model = Post
        only = 'slug', 'title', 'content'
