import logging

from sqlalchemy.orm import Session

from app.conf.config import settings
from app.contrib.auth.repository import user_repo

logger = logging.getLogger(__name__)


# make sure all SQL Alchemy models are imported (app.db.base) before initializing DB
# otherwise, SQL Alchemy might fail to initialize relationships properly
# for more details: https://github.com/tiangolo/full-stack-fastapi-postgresql/issues/28


def init_db(db: Session) -> None:
    # Tables should be created with Alembic migrations
    # But if you don't want to use migrations, create
    # the tables un-commenting the next line
    # Base.metadata.create_all(bind=engine)
    user = user_repo.get_by_email(db, email=settings.FIRST_SUPERUSER)

    if not user:
        user_in ={
            'email': settings.FIRST_SUPERUSER,
            'password': settings.FIRST_SUPERUSER_PASSWORD
        }

        user = user_repo.create(db, obj_in=user_in)  # noqa: F841
        logger.info("User successfully created")
