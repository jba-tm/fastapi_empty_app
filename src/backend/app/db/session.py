from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.conf.config import settings

engine = create_engine(settings.SQLALCHEMY_DATABASE_URI, pool_pre_ping=True, connect_args={"check_same_thread": False} )
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    # twophase=True,
    bind=engine, )

