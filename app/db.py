import logging
import time

from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import declarative_base, sessionmaker

from .config import settings

logger = logging.getLogger("linkly")

connect_args = {}
if settings.database_url.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    settings.database_url,
    connect_args=connect_args,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db(retries=15, delay=2):
    for attempt in range(1, retries + 1):
        try:
            Base.metadata.create_all(bind=engine)
            return
        except OperationalError:
            if attempt == retries:
                raise
            logger.warning("database not reachable yet, retry %s/%s", attempt, retries)
            time.sleep(delay)
