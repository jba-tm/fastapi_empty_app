import logging
from dotenv import load_dotenv, dotenv_values


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init() -> None:
    from app.db.init_db import init_db
    from app.db.session import SessionLocal
    db = SessionLocal()
    init_db(db)


def main() -> None:
    logger.info("Creating initial data")
    init()
    logger.info("Initial data created")


if __name__ == "__main__":
    load_dotenv('.env')
    main()
