import logging
from datetime import datetime

from fastapi import Request
from fastapi.templating import Jinja2Templates as BaseJinja2Templates
from typing import Any
from starlette_i18n import gettext_lazy as _, get_locale_code
from gettext import ngettext

from app.conf.config import structure_settings
from app.utils.urls import include_query_params

try:
    import jinja2

    # @contextfunction renamed to @pass_context in Jinja 3.0, to be removed in 3.1
    if hasattr(jinja2, "pass_context"):
        pass_context = jinja2.pass_context
    else:  # pragma: nocover
        pass_context = jinja2.contextfunction
except ImportError:  # pragma: nocover
    jinja2 = None  # type: ignore


def flash(request: Request, message: Any, category: str = "success") -> None:
    if "_messages" not in request.session:
        request.session["_messages"] = []
        request.session["_messages"].append({"message": message, "category": category})


def get_page_total(total: int, limit: int) -> int:
    return int(total / limit) + (total % limit > 0)


def get_flashed_messages(request: Request):
    # print(request.session)
    return request.session.pop("_messages") if "_messages" in request.session else []


class SilentUndefined(jinja2.Undefined):
    """
    Dont break page loads because vars arent there!
    """

    def _fail_with_undefined_error(self, *args, **kwargs):
        logging.exception('JINJA2: something was undefined!')
        return ''


class Jinja2Templates(BaseJinja2Templates):
    def _create_env(self, directory: str) -> "jinja2.Environment":
        env = super()._create_env(directory)
        loader = jinja2.FileSystemLoader(directory)

        env.undefined = SilentUndefined
        env.loader = loader

        env.autoescape = True
        env.add_extension('jinja2.ext.i18n')
        env.add_extension('jinja2.ext.autoescape')

        env.install_gettext_callables(gettext=_, ngettext=ngettext)  # type: ignore

        env.globals['get_current_language'] = get_locale_code
        env.globals['get_flashed_messages'] = get_flashed_messages
        env.globals['get_page_total'] = get_page_total

        env.globals['include_query_params'] = include_query_params
        env.globals['now'] = datetime.now

        return env


templates = Jinja2Templates(directory=structure_settings.TEMPLATES.get('DIR', 'templates'))
