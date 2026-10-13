from pathlib import Path

import pytest
from sqlalchemy import inspect, text
from sqlalchemy.orm import Mapped, Session, mapped_column

from app import database
from app.database_config import DATABASE_PATH, DATABASE_URL, create_sqlite_engine


def test_database_path_is_absolute_and_backend_owned(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    expected_path = (Path(__file__).resolve().parents[1] / "data" / "speakspark.db").resolve()
    monkeypatch.chdir(tmp_path)

    assert DATABASE_PATH == expected_path
    assert DATABASE_PATH.is_absolute()
    assert Path(DATABASE_URL.database) == expected_path


def test_schema_initialization_creates_sqlite_file_and_is_repeatable(tmp_path: Path) -> None:
    database_path = tmp_path / "isolated" / "speakspark.db"
    isolated_engine = create_sqlite_engine(database_path)

    class SchemaProbe(database.Base):
        __tablename__ = "schema_probe"

        id: Mapped[int] = mapped_column(primary_key=True)

    try:
        assert not database_path.exists()

        database.init_db(bind=isolated_engine)
        expected_tables = set(database.Base.metadata.tables)
        assert database_path.is_file()
        assert set(inspect(isolated_engine).get_table_names()) == expected_tables
        assert "schema_probe" in expected_tables

        database.init_db(bind=isolated_engine)
        assert set(inspect(isolated_engine).get_table_names()) == expected_tables
    finally:
        database.Base.metadata.remove(SchemaProbe.__table__)
        isolated_engine.dispose()


def test_request_session_persists_data_and_closes_after_exception(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    isolated_engine = create_sqlite_engine(tmp_path / "session.sqlite")
    created_sessions: list[Session] = []

    class TrackedSession(Session):
        was_closed = False

        def close(self) -> None:
            self.was_closed = True
            super().close()

    def create_session() -> Session:
        session = TrackedSession(bind=isolated_engine)
        created_sessions.append(session)
        return session

    monkeypatch.setattr(database, "SessionLocal", create_session)

    try:
        request_session = database.get_db()
        session = next(request_session)
        session.execute(text("CREATE TABLE session_probe (value TEXT NOT NULL)"))
        session.execute(text("INSERT INTO session_probe (value) VALUES ('persisted')"))
        session.commit()

        class RequestFailure(Exception):
            pass

        with pytest.raises(RequestFailure):
            request_session.throw(RequestFailure())

        assert created_sessions[0].was_closed
        with isolated_engine.connect() as connection:
            assert connection.scalar(text("SELECT value FROM session_probe")) == "persisted"
    finally:
        isolated_engine.dispose()
