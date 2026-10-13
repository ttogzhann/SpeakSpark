from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import inspect, select
from sqlalchemy.orm import Session

from app import database, main
from app.database_config import create_sqlite_engine
from app.models import BuiltInActivity


def test_health_endpoint_initializes_isolated_database(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    database_path = tmp_path / "startup" / "speakspark.db"
    isolated_engine = create_sqlite_engine(database_path)
    initialize_schema = database.init_db
    monkeypatch.setattr(database, "init_db", lambda: initialize_schema(bind=isolated_engine))

    try:
        with TestClient(main.app) as client:
            response = client.get("/health")

        assert response.status_code == 200
        assert response.text == '{"status":"ok"}'
        assert response.json() == {"status": "ok"}
        assert database_path.is_file()
        assert set(inspect(isolated_engine).get_table_names()) == set(database.Base.metadata.tables)
        with Session(isolated_engine) as session:
            assert len(session.scalars(select(BuiltInActivity.id)).all()) == 36
    finally:
        isolated_engine.dispose()


def test_database_uses_sqlite() -> None:
    assert database.engine.dialect.name == "sqlite"
