import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

_sql_echo = os.getenv("SQL_ECHO", "").lower() in ("1", "true", "yes")
if not _sql_echo:
    _sql_echo = os.getenv("ENVIRONMENT", "development") == "development"

engine = create_engine(DATABASE_URL, echo=_sql_echo)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
