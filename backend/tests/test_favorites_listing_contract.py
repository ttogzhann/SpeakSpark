from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.database_config import create_sqlite_engine
from app.main import app
from app.models import BuiltInActivity, CustomActivity, Favorite


@pytest.fixture
def favorites_client(tmp_path: Path):
    engine = create_sqlite_engine(tmp_path / "favorites-contract.sqlite")
    Base.metadata.create_all(bind=engine)
    session_factory = sessionmaker(bind=engine)

    def get_test_db():
        with session_factory() as session:
            yield session

    previous_override = app.dependency_overrides.get(get_db)
    app.dependency_overrides[get_db] = get_test_db
    try:
        yield TestClient(app), session_factory
    finally:
        if previous_override is None:
            app.dependency_overrides.pop(get_db, None)
        else:
            app.dependency_overrides[get_db] = previous_override
        engine.dispose()


def seed_library(session_factory):
    with session_factory() as session:
        session.add_all([
            BuiltInActivity(
                id="builtin-saved", title="Saved card", level="A1",
                topic="Daily Life", type="Conversation Card", prompt="Describe your day.",
            ),
            BuiltInActivity(
                id="builtin-unsaved", title="Unsaved card", level="A2",
                topic="Food", type="Conversation Card", prompt="Describe lunch.",
            ),
            CustomActivity(
                id="custom-saved", title="Saved role-play", level="B1",
                topic="Work", type="Role-play", prompt="Plan a project.",
                follow_up_questions=["What comes next?"],
                useful_phrases=["Shall we begin?"],
                roles=[{"participant": "Tutor", "objective": "Agree on a plan."}],
                instructions=["Take turns."],
            ),
            CustomActivity(
                id="custom-unsaved", title="Unsaved challenge", level="B2",
                topic="Travel", type="Speaking Challenge", prompt="Plan a trip.",
            ),
        ])
        session.commit()


def database_snapshot(session_factory):
    with session_factory() as session:
        return {
            model.__tablename__: [
                {column.name: getattr(record, column.name) for column in model.__table__.columns}
                for record in session.scalars(select(model)).all()
            ]
            for model in (BuiltInActivity, CustomActivity, Favorite)
        }


def test_mixed_favorites_preserve_shared_contract_and_read_only_storage(favorites_client):
    client, session_factory = favorites_client
    seed_library(session_factory)
    for activity_id in ("builtin-saved", "custom-saved"):
        assert client.post("/favorites", json={"activity_id": activity_id}).status_code == 201

    before = database_snapshot(session_factory)
    response = client.get("/favorites")
    assert response.status_code == 200
    records = response.json()
    assert len(records) == 2
    by_id = {record["id"]: record for record in records}
    assert set(by_id) == {"builtin-saved", "custom-saved"}
    expected_keys = {
        "id", "is_builtin", "title", "level", "topic", "type", "prompt",
        "follow_up_questions", "useful_phrases", "roles", "instructions",
    }
    library = {record["id"]: record for record in client.get("/activities").json()}
    for record in records:
        assert set(record) == expected_keys
        assert record == library[record["id"]]
        assert record == client.get(f"/activities/{record['id']}").json()
    assert by_id["builtin-saved"]["is_builtin"] is True
    assert by_id["custom-saved"]["is_builtin"] is False
    for field in ("follow_up_questions", "useful_phrases", "roles", "instructions"):
        assert by_id["builtin-saved"][field] == []
    assert by_id["custom-saved"]["follow_up_questions"] == ["What comes next?"]
    assert by_id["custom-saved"]["useful_phrases"] == ["Shall we begin?"]
    assert by_id["custom-saved"]["roles"] == [
        {"participant": "Tutor", "objective": "Agree on a plan."}
    ]
    assert by_id["custom-saved"]["instructions"] == ["Take turns."]
    assert database_snapshot(session_factory) == before
    assert TestClient(app).get("/favorites").json() == records


def test_empty_favorites_with_populated_library(favorites_client):
    client, session_factory = favorites_client
    seed_library(session_factory)
    before = database_snapshot(session_factory)
    response = client.get("/favorites")
    assert response.status_code == 200
    assert response.json() == []
    assert database_snapshot(session_factory) == before


def test_api_deletion_removes_custom_favorite_and_keeps_unrelated_favorite(favorites_client):
    client, session_factory = favorites_client
    seed_library(session_factory)
    for activity_id in ("builtin-saved", "custom-saved"):
        assert client.post("/favorites", json={"activity_id": activity_id}).status_code == 201
    before = {record["id"]: record for record in client.get("/favorites").json()}

    assert client.delete("/activities/custom-saved").status_code == 204
    response = client.get("/favorites")
    assert response.status_code == 200
    assert response.json() == [before["builtin-saved"]]
    with session_factory() as session:
        assert session.get(CustomActivity, "custom-saved") is None
        assert session.get(Favorite, "custom-saved") is None
        assert session.get(Favorite, "builtin-saved") is not None
