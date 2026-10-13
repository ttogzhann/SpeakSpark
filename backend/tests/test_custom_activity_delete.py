from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session, sessionmaker

from app.database import Base, get_db
from app.database_config import create_sqlite_engine
from app.main import app
from app.models import BuiltInActivity, CustomActivity, Favorite


@pytest.fixture
def activity_client(
    tmp_path: Path,
):
    engine = create_sqlite_engine(tmp_path / "custom-delete.sqlite")
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


def test_deletes_custom_activity_and_its_favorites(activity_client) -> None:
    client, session_factory = activity_client
    custom_id = "custom-delete-123"
    with session_factory() as session:
        session.add(
            CustomActivity(
                id=custom_id,
                title="Delete me",
                level="A2",
                topic="Travel",
                type="Conversation Card",
                prompt="Describe a trip.",
            )
        )
        session.add_all(
            [
                Favorite(activity_id=custom_id),
                Favorite(activity_id="custom-stays"),
            ]
        )
        session.commit()

    delete_response = client.delete(f"/activities/{custom_id}")

    assert delete_response.status_code == 204
    assert delete_response.content == b""
    assert client.get("/activities").status_code == 200
    assert client.get(f"/activities/{custom_id}").status_code == 404

    with session_factory() as session:
        assert session.get(CustomActivity, custom_id) is None
        assert session.get(Favorite, custom_id) is None
        assert session.get(Favorite, "custom-stays") is not None


def test_rejects_builtin_delete_and_unknown_ids_without_mutating_data(
    activity_client,
) -> None:
    client, session_factory = activity_client
    with session_factory() as session:
        session.add(
            BuiltInActivity(
                id="builtin-delete-keep",
                title="Keep me",
                level="B1",
                topic="Food",
                type="Speaking Challenge",
                prompt="Keep this built-in alive.",
            )
        )
        session.commit()

    built_in_response = client.delete("/activities/builtin-delete-keep")
    missing_response = client.delete("/activities/custom-missing-delete-id")

    assert built_in_response.status_code == 400
    assert missing_response.status_code == 404

    with session_factory() as session:
        assert session.get(BuiltInActivity, "builtin-delete-keep") is not None


def test_repeat_delete_of_same_custom_activity_returns_not_found(
    activity_client,
) -> None:
    client, session_factory = activity_client
    custom_id = "custom-delete-repeat"
    with session_factory() as session:
        session.add(
            CustomActivity(
                id=custom_id,
                title="One-time item",
                level="A1",
                topic="Daily Life",
                type="Role-play",
                prompt="Talk about your day.",
            )
        )
        session.commit()

    first_response = client.delete(f"/activities/{custom_id}")
    second_response = client.delete(f"/activities/{custom_id}")

    assert first_response.status_code == 204
    assert second_response.status_code == 404
