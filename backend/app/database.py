from collections.abc import Generator

from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Session

from app.database_config import DATABASE_PATH, DATABASE_URL, SessionLocal, engine


class Base(DeclarativeBase):
    pass


def init_db(bind: Engine | None = None) -> None:
    from app import models  # noqa: F401

    Base.metadata.create_all(bind=bind if bind is not None else engine)


def get_db() -> Generator[Session, None, None]:
    with SessionLocal() as session:
        yield session
