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
    engine = create_sqlite_engine(tmp_path / "custom-update.sqlite")
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


def test_updates_existing_custom_activity_and_reflects_in_list_and_detail(
    activity_client,
) -> None:
    client, session_factory = activity_client
    with session_factory() as session:
        session.add(
            CustomActivity(
                id="custom-123",
                title="Old title",
                level="A1",
                topic="Daily Life",
                type="Conversation Card",
                prompt="Old prompt",
                follow_up_questions=["Old question"],
            )
        )
        session.commit()

    payload = {
        "title": "New title",
        "level": "B2",
        "topic": "Travel",
        "type": "Role-play",
        "prompt": "New prompt",
        "roles": [{"participant": "Traveler", "objective": "Ask for directions."}],
        "useful_phrases": ["Could you help me?"],
        "instructions": ["Take turns."],
    }

    response = client.put("/activities/custom-123", json=payload)

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == "custom-123"
    assert body["title"] == "New title"
    assert body["level"] == "B2"
    assert body["topic"] == "Travel"
    assert body["type"] == "Role-play"
    assert body["prompt"] == "New prompt"
    assert body["roles"] == [{"participant": "Traveler", "objective": "Ask for directions."}]
    assert body["useful_phrases"] == ["Could you help me?"]
    assert body["instructions"] == ["Take turns."]

    list_response = client.get("/activities")
    detail_response = client.get("/activities/custom-123")
    assert list_response.status_code == 200
    assert detail_response.status_code == 200
    assert any(item["id"] == "custom-123" and item["title"] == "New title" for item in list_response.json())
    assert detail_response.json()["title"] == "New title"


def test_rejects_invalid_update_payload_without_partial_persistence(
    activity_client,
) -> None:
    client, session_factory = activity_client
    with session_factory() as session:
        session.add(
            CustomActivity(
                id="custom-456",
                title="Original title",
                level="A1",
                topic="Work",
                type="Speaking Challenge",
                prompt="Original prompt",
            )
        )
        session.commit()

    payload = {
        "title": "   ",
        "level": "A1",
        "topic": "Work",
        "type": "Speaking Challenge",
        "prompt": "Still valid",
    }

    response = client.put("/activities/custom-456", json=payload)

    assert response.status_code == 422

    with session_factory() as session:
        saved = session.get(CustomActivity, "custom-456")
        assert saved is not None
        assert saved.title == "Original title"
        assert saved.prompt == "Original prompt"


def test_unknown_id_and_builtin_activity_updates_are_rejected(
    activity_client,
) -> None:
    client, session_factory = activity_client
    with session_factory() as session:
        session.add(
            BuiltInActivity(
                id="builtin-keep",
                title="Keep me",
                level="A2",
                topic="Daily Life",
                type="Conversation Card",
                prompt="Keep me unchanged.",
            )
        )
        session.commit()

    missing_response = client.put(
        "/activities/missing-id",
        json={
            "title": "Nope",
            "level": "A1",
            "topic": "Food",
            "type": "Conversation Card",
            "prompt": "Nope.",
        },
    )
    built_in_response = client.put(
        "/activities/builtin-keep",
        json={
            "title": "Try to change built-in",
            "level": "A1",
            "topic": "Food",
            "type": "Conversation Card",
            "prompt": "This should fail.",
        },
    )

    assert missing_response.status_code == 404
    assert built_in_response.status_code == 400

    with session_factory() as session:
        built_in = session.get(BuiltInActivity, "builtin-keep")
        assert built_in is not None
        assert built_in.title == "Keep me"
