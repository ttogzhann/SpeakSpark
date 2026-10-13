from collections.abc import Iterator
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


def test_lists_builtin_and_custom_activities_with_all_fields(
    activity_client: tuple[TestClient, sessionmaker[Session]],
) -> None:
    client, session_factory = activity_client
    with session_factory() as session:
        session.add_all(
            [
                BuiltInActivity(
                    id="builtin-card-01",
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
                CustomActivity(
                    id="custom-roleplay-01",
                    title="A custom role-play",
                    level="B1",
                    topic="Work",
                    type="Role-play",
                    prompt="Discuss a new project with a colleague.",
                    follow_up_questions=["What is your first step?"],
                    useful_phrases=["How about...?", "I suggest..."],
                    roles=[
                        {"participant": "Colleague A", "objective": "Suggest a plan."},
                        {"participant": "Colleague B", "objective": "Ask questions."},
                    ],
                    instructions=["Take turns sharing ideas."],
                ),
            ]
        )
        session.commit()

    response = client.get("/activities")

    assert response.status_code == 200
    assert response.json() == [
        {
            "id": "builtin-card-01",
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
        },
        {
            "id": "custom-roleplay-01",
            "is_builtin": False,
            "title": "A custom role-play",
            "level": "B1",
            "topic": "Work",
            "type": "Role-play",
            "prompt": "Discuss a new project with a colleague.",
            "follow_up_questions": ["What is your first step?"],
            "useful_phrases": ["How about...?", "I suggest..."],
            "roles": [
                {"participant": "Colleague A", "objective": "Suggest a plan."},
                {"participant": "Colleague B", "objective": "Ask questions."},
            ],
            "instructions": ["Take turns sharing ideas."],
        },
    ]


def test_missing_optional_fields_are_serialized_as_empty_arrays(
    activity_client: tuple[TestClient, sessionmaker[Session]],
) -> None:
    client, session_factory = activity_client
    with session_factory() as session:
        session.add(
            CustomActivity(
                id="custom-no-guidance",
                title="Describe your neighborhood",
                level="A2",
                topic="Daily Life",
                type="Speaking Challenge",
                prompt="Describe a place you like in your neighborhood.",
            )
        )
        session.commit()

    response = client.get("/activities")

    assert response.status_code == 200
    assert response.json() == [
        {
            "id": "custom-no-guidance",
            "is_builtin": False,
            "title": "Describe your neighborhood",
            "level": "A2",
            "topic": "Daily Life",
            "type": "Speaking Challenge",
            "prompt": "Describe a place you like in your neighborhood.",
            "follow_up_questions": [],
            "useful_phrases": [],
            "roles": [],
            "instructions": [],
        }
    ]


def test_empty_database_returns_empty_array(
    activity_client: tuple[TestClient, sessionmaker[Session]],
) -> None:
    client, _ = activity_client

    response = client.get("/activities")

    assert response.status_code == 200
    assert response.json() == []


def test_activity_listing_does_not_require_authentication(
    activity_client: tuple[TestClient, sessionmaker[Session]],
) -> None:
    client, _ = activity_client

    response = client.get("/activities")

    assert response.status_code == 200
