from typing import Generator, Optional, Union, TYPE_CHECKING

from fastapi import Depends, Request
from starlette.authentication import BaseUser

from app.conf.config import settings
from app.core.exceptions import UnAuthenticated
from app.db.session import SessionLocal

if TYPE_CHECKING:
    from app.contrib.auth.models import User


def get_db() -> "Generator":
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
        request: "Request",
) -> "BaseUser":
    """
    Get user by token
    :param request: Request
    :return:
    """
    return request.user


def get_authenticated_user(user: "BaseUser" = Depends(get_current_user)) -> "User":
    """
    Get authenticated user for if not redirect to login page
    :param user:
    :return:
    """
    if user.is_authenticated:
        return user.user
    raise UnAuthenticated


async def get_commons(
        order_by: Optional[str] = None,
        offset: Optional[int] = None,
        limit: Optional[int] = settings.PAGINATION_MAX_SIZE,
        page: Optional[int] = 1,
) -> dict:
    """
    Get commons dict for list pagination and filter
    :param order_by:
    :param offset:
    :param limit:
    :param page:
    :return:
    """
    if order_by is None:
        order_by = []
    elif isinstance(order_by, str):
        order_by = order_by.split(',')
    if offset is None and page is None:
        offset = 0
    elif offset is None and page:
        if page <= 0:
            page = 1
        offset = (page - 1) * limit
    return {'limit': limit, 'offset': offset, 'order_by': order_by, 'page': page}
