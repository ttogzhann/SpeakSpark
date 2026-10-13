from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session, sessionmaker

from app.database import Base, get_db
from app.database_config import create_sqlite_engine
from app.main import app
from app.models import BuiltInActivity, CustomActivity


def _seed_filter_activities(session_factory: sessionmaker[Session]) -> None:
    with session_factory() as session:
        session.add_all(
            [
                BuiltInActivity(
                    id="builtin-filter-a1",
                    title="A1 daily card",
                    level="A1",
                    topic="Daily Life",
                    type="Conversation Card",
                    prompt="Describe your morning.",
                ),
                CustomActivity(
                    id="custom-filter-b1",
                    title="B1 work role-play",
                    level="B1",
                    topic="Work",
                    type="Role-play",
                    prompt="Plan a project with a colleague.",
                ),
                BuiltInActivity(
                    id="builtin-filter-a2",
                    title="A2 travel challenge",
                    level="A2",
                    topic="Travel",
                    type="Speaking Challenge",
                    prompt="Describe a journey.",
                ),
                CustomActivity(
                    id="custom-filter-a1",
                    title="A1 custom discussion",
                    level="A1",
                    topic="Food",
                    type="Conversation Card",
                    prompt="What food do you enjoy?",
                ),
            ]
        )
        session.commit()


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

@pytest.mark.parametrize(
    ("filter_parameter", "filter_value", "expected_matches"),
    [
        (
            "level",
            "A1",
            [("builtin-filter-a1", True), ("custom-filter-a1", False)],
        ),
        ("topic", "Work", [("custom-filter-b1", False)]),
        ("type", "Speaking Challenges", [("builtin-filter-a2", True)]),
    ],
)
def test_activity_listing_filters_by_each_supported_dimension(
    activity_client: tuple[TestClient, sessionmaker[Session]],
    filter_parameter: str,
    filter_value: str,
    expected_matches: list[tuple[str, bool]],
) -> None:
    client, session_factory = activity_client
    _seed_filter_activities(session_factory)

    response = client.get("/activities", params={filter_parameter: filter_value})

    assert response.status_code == 200
    assert [
        (activity["id"], activity["is_builtin"]) for activity in response.json()
    ] == expected_matches


def test_activity_listing_combines_filters_with_and_logic(
    activity_client: tuple[TestClient, sessionmaker[Session]],
) -> None:
    client, session_factory = activity_client
    _seed_filter_activities(session_factory)

    response = client.get(
        "/activities",
        params={"level": "B1", "topic": "Work", "type": "Role-play"},
    )

    assert response.status_code == 200
    assert [activity["id"] for activity in response.json()] == ["custom-filter-b1"]

    response = client.get(
        "/activities", params={"level": "B1", "topic": "Work"}
    )

    assert response.status_code == 200
    assert [activity["id"] for activity in response.json()] == ["custom-filter-b1"]


def test_activity_listing_returns_matching_builtin_and_custom_activities(
    activity_client: tuple[TestClient, sessionmaker[Session]],
) -> None:
    client, session_factory = activity_client
    _seed_filter_activities(session_factory)

    response = client.get("/activities", params={"level": "A1"})

    assert response.status_code == 200
    assert [
        (activity["id"], activity["is_builtin"]) for activity in response.json()
    ] == [("builtin-filter-a1", True), ("custom-filter-a1", False)]


def test_activity_listing_leaves_omitted_filters_unrestricted(
    activity_client: tuple[TestClient, sessionmaker[Session]],
) -> None:
    client, session_factory = activity_client
    _seed_filter_activities(session_factory)

    response = client.get("/activities", params={"topic": "Travel"})

    assert response.status_code == 200
    assert [activity["id"] for activity in response.json()] == ["builtin-filter-a2"]


def test_activity_listing_returns_empty_array_when_valid_filters_do_not_match(
    activity_client: tuple[TestClient, sessionmaker[Session]],
) -> None:
    client, session_factory = activity_client
    _seed_filter_activities(session_factory)

    response = client.get("/activities", params={"level": "B2"})

    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.parametrize(
    ("filter_parameter", "invalid_value"),
    [("level", "C1"), ("topic", "Sports"), ("type", "Unsupported Type")],
)
def test_activity_listing_rejects_invalid_filter_values(
    activity_client: tuple[TestClient, sessionmaker[Session]],
    filter_parameter: str,
    invalid_value: str,
) -> None:
    client, session_factory = activity_client
    _seed_filter_activities(session_factory)

    response = client.get("/activities", params={filter_parameter: invalid_value})

    assert response.status_code == 422
