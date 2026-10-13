from collections.abc import Generator

from sqlalchemy.engine import Engine
from sqlalchemy import text
from sqlalchemy.orm import DeclarativeBase, Session

from app.database_config import DATABASE_PATH, DATABASE_URL, SessionLocal, engine


class Base(DeclarativeBase):
    pass


def init_db(bind: Engine | None = None) -> None:
    from app import models  # noqa: F401
    from app.builtin_activities import seed_builtin_activities

    target_engine = bind if bind is not None else engine
    Base.metadata.create_all(bind=target_engine)
    if target_engine.dialect.name == "sqlite":
        with target_engine.begin() as connection:
            connection.execute(
                text(
                    """
                    CREATE TRIGGER IF NOT EXISTS built_in_activities_no_update
                    BEFORE UPDATE ON built_in_activities
                    BEGIN
                        SELECT RAISE(ABORT, 'Built-in activities are read-only');
                    END
                    """
                )
            )
            connection.execute(
                text(
                    """
                    CREATE TRIGGER IF NOT EXISTS built_in_activities_no_delete
                    BEFORE DELETE ON built_in_activities
                    BEGIN
                        SELECT RAISE(ABORT, 'Built-in activities are read-only');
                    END
                    """
                )
            )

    with Session(bind=target_engine) as session:
        seed_builtin_activities(session)


def get_db() -> Generator[Session, None, None]:
    with SessionLocal() as session:
        yield session
