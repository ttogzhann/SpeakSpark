from collections.abc import Iterator
from pathlib import Path
from uuid import uuid4

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
) -> Iterator[tuple[TestClient, sessionmaker[Session]]]:
    engine = create_sqlite_engine(tmp_path / "activities.sqlite")
    Base.metadata.create_all(bind=engine)
    test_session_factory = sessionmaker(bind=engine)

    def get_test_db() -> Iterator[Session]:
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


def test_gets_requested_builtin_activity_with_shared_response_shape(
    activity_client: tuple[TestClient, sessionmaker[Session]],
) -> None:
    client, session_factory = activity_client
    with session_factory() as session:
        session.add_all(
            [
                BuiltInActivity(
                    id="builtin-card-daily-life-01",
                    title="A built-in conversation",
                    level="A1",
                    topic="Daily Life",
                    type="Conversation Card",
                    prompt="What do you do every morning?",
                    follow_up_questions=["What do you do first?"],
                    useful_phrases=["I usually..."],
                    roles=[],
                    instructions=[],
                ),
                BuiltInActivity(
                    id="builtin-card-travel-01",
                    title="Another activity",
                    level="A2",
                    topic="Travel",
                    type="Conversation Card",
                    prompt="Where would you like to travel?",
                ),
            ]
        )
        session.commit()

    response = client.get("/activities/builtin-card-daily-life-01")

    assert response.status_code == 200
    assert response.json() == {
        "id": "builtin-card-daily-life-01",
        "is_builtin": True,
        "title": "A built-in conversation",
        "level": "A1",
        "topic": "Daily Life",
        "type": "Conversation Card",
        "prompt": "What do you do every morning?",
        "follow_up_questions": ["What do you do first?"],
        "useful_phrases": ["I usually..."],
        "roles": [],
        "instructions": [],
    }


def test_gets_requested_custom_activity_and_empty_optional_fields(
    activity_client: tuple[TestClient, sessionmaker[Session]],
) -> None:
    client, session_factory = activity_client
    activity_id = str(uuid4())
    with session_factory() as session:
        session.add(
            CustomActivity(
                id=activity_id,
                title="A custom role-play",
                level="B1",
                topic="Work",
                type="Role-play",
                prompt="Discuss a new project with a colleague.",
                useful_phrases=["How about...?", "I suggest..."],
                roles=[
                    {"participant": "Colleague A", "objective": "Suggest a plan."},
                    {"participant": "Colleague B", "objective": "Ask questions."},
                ],
                instructions=["Take turns sharing ideas."],
            )
        )
        session.commit()

    response = client.get(f"/activities/{activity_id}")

    assert response.status_code == 200
    assert response.json() == {
        "id": activity_id,
        "is_builtin": False,
        "title": "A custom role-play",
        "level": "B1",
        "topic": "Work",
        "type": "Role-play",
        "prompt": "Discuss a new project with a colleague.",
        "follow_up_questions": [],
        "useful_phrases": ["How about...?", "I suggest..."],
        "roles": [
            {"participant": "Colleague A", "objective": "Suggest a plan."},
            {"participant": "Colleague B", "objective": "Ask questions."},
        ],
        "instructions": ["Take turns sharing ideas."],
    }


def test_unknown_valid_activity_id_returns_404(
    activity_client: tuple[TestClient, sessionmaker[Session]],
) -> None:
    client, _ = activity_client

    response = client.get("/activities/builtin-card-does-not-exist-99")

    assert response.status_code == 404


def test_malformed_activity_id_returns_422(
    activity_client: tuple[TestClient, sessionmaker[Session]],
) -> None:
    client, _ = activity_client

    response = client.get("/activities/not-an-activity-id")

    assert response.status_code == 422


def test_get_activity_does_not_require_authentication(
    activity_client: tuple[TestClient, sessionmaker[Session]],
) -> None:
    client, session_factory = activity_client
    with session_factory() as session:
        session.add(
            BuiltInActivity(
                id="builtin-card-auth-check-01",
                title="No login needed",
                level="A1",
                topic="Daily Life",
                type="Conversation Card",
                prompt="What do you like?",
            )
        )
        session.commit()

    response = client.get("/activities/builtin-card-auth-check-01")

    assert response.status_code == 200
