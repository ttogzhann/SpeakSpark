from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session, sessionmaker

from app.database import Base, get_db
from app.database_config import create_sqlite_engine
from app.main import app
from app.models import BuiltInActivity, CustomActivity


@pytest.fixture
def activity_client(
    tmp_path: Path,
):
    engine = create_sqlite_engine(tmp_path / "custom-create.sqlite")
    Base.metadata.create_all(bind=engine)
    test_session_factory = sessionmaker(bind=engine)

    def get_test_db():
        with test_session_factory() as session:
            yield session

    previous_override = app.dependency_overrides.get(get_db)
    app.dependency_overrides[get_db] = get_test_db
    try:
        yield TestClient(app), test_session_factory
    finally:
        if previous_override is None:
            app.dependency_overrides.pop(get_db, None)
        else:
            app.dependency_overrides[get_db] = previous_override
        engine.dispose()


def test_creates_valid_custom_activity_and_returns_persisted_record(
    activity_client,
) -> None:
    client, session_factory = activity_client
    payload = {
        "title": "A weekend plan",
        "level": "A2",
        "topic": "Daily Life",
        "type": "Role-play",
        "prompt": "Plan a weekend with a friend.",
        "roles": [
            {"participant": "Friend A", "objective": "Suggest activities."},
            {"participant": "Friend B", "objective": "Ask questions and agree."},
        ],
        "useful_phrases": ["How about...?"] ,
    }

    response = client.post("/activities", json=payload)

    assert response.status_code == 201
    body = response.json()
    assert body["is_builtin"] is False
    assert body["title"] == payload["title"]
    assert body["level"] == payload["level"]
    assert body["topic"] == payload["topic"]
    assert body["type"] == payload["type"]
    assert body["prompt"] == payload["prompt"]
    assert body["roles"] == payload["roles"]
    assert body["useful_phrases"] == payload["useful_phrases"]
    assert body["follow_up_questions"] == []
    assert body["instructions"] == []

    with session_factory() as session:
        created = session.get(CustomActivity, body["id"])
        assert created is not None
        assert created.title == payload["title"]


def test_created_custom_activity_appears_in_list_and_detail_endpoints(
    activity_client,
) -> None:
    client, _ = activity_client
    payload = {
        "title": "Coffee shop chat",
        "level": "B1",
        "topic": "Food",
        "type": "Conversation Card",
        "prompt": "Talk about your favorite café.",
        "follow_up_questions": ["What do you order?"],
    }

    create_response = client.post("/activities", json=payload)
    created_id = create_response.json()["id"]

    list_response = client.get("/activities")
    detail_response = client.get(f"/activities/{created_id}")

    assert create_response.status_code == 201
    assert list_response.status_code == 200
    assert detail_response.status_code == 200
    assert any(item["id"] == created_id for item in list_response.json())
    assert detail_response.json()["id"] == created_id
    assert detail_response.json()["is_builtin"] is False


def test_custom_creation_rejects_missing_or_invalid_payloads_without_persisting(
    activity_client,
) -> None:
    client, session_factory = activity_client

    invalid_cases = [
        {"title": "A", "level": "A1", "topic": "Daily Life", "type": "Conversation Card"},
        {"title": "   ", "level": "A1", "topic": "Daily Life", "type": "Conversation Card", "prompt": "Prompt"},
        {"title": "A", "level": "A1", "topic": "Daily Life", "type": "Invalid", "prompt": "Prompt"},
        {"title": "A", "level": "A1", "topic": "Daily Life", "type": "Conversation Card", "prompt": "Prompt", "roles": [{"participant": "Student"}]},
        {"title": "A", "level": "A1", "topic": "Daily Life", "type": "Conversation Card", "prompt": "Prompt", "unexpected": True},
    ]

    for payload in invalid_cases:
        response = client.post("/activities", json=payload)
        assert response.status_code == 422

    with session_factory() as session:
        assert session.query(CustomActivity).count() == 0


def test_custom_creation_preserves_builtins_and_allows_missing_optional_fields(
    activity_client,
) -> None:
    client, session_factory = activity_client
    with session_factory() as session:
        session.add(
            BuiltInActivity(
                id="builtin-existing-01",
                title="Built-in title",
                level="A1",
                topic="Daily Life",
                type="Conversation Card",
                prompt="What do you do after work?",
            )
        )
        session.commit()

    payload = {
        "title": "New custom task",
        "level": "B2",
        "topic": "Technology",
        "type": "Speaking Challenge",
        "prompt": "Describe a tool that changed your life.",
    }

    response = client.post("/activities", json=payload)
    assert response.status_code == 201

    with session_factory() as session:
        builtin_count = session.query(BuiltInActivity).count()
        custom_count = session.query(CustomActivity).count()
        assert builtin_count == 1
        assert custom_count == 1


def test_custom_creation_does_not_require_authentication(activity_client) -> None:
    client, _ = activity_client
    payload = {
        "title": "No login needed",
        "level": "A1",
        "topic": "Travel",
        "type": "Conversation Card",
        "prompt": "Talk about a place you visited.",
    }

    response = client.post("/activities", json=payload)

    assert response.status_code == 201
