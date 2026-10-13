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
    engine = create_sqlite_engine(tmp_path / "favorites.sqlite")
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


def test_creates_favorite_for_existing_builtin_and_custom_activity(activity_client) -> None:
    client, session_factory = activity_client
    with session_factory() as session:
        session.add(
            BuiltInActivity(
                id="builtin-favorite-01",
                title="Built-in favorite",
                level="A1",
                topic="Daily Life",
                type="Conversation Card",
                prompt="Tell me about your routine.",
            )
        )
        session.add(
            CustomActivity(
                id="custom-favorite-01",
                title="Custom favorite",
                level="B2",
                topic="Technology",
                type="Role-play",
                prompt="Describe a product launch.",
            )
        )
        session.commit()

    builtin_response = client.post("/favorites", json={"activity_id": "builtin-favorite-01"})
    custom_response = client.post("/favorites", json={"activity_id": "custom-favorite-01"})

    assert builtin_response.status_code == 201
    assert custom_response.status_code == 201
    assert builtin_response.json() == {"activity_id": "builtin-favorite-01"}
    assert custom_response.json() == {"activity_id": "custom-favorite-01"}

    with session_factory() as session:
        assert session.get(Favorite, "builtin-favorite-01") is not None
        assert session.get(Favorite, "custom-favorite-01") is not None


def test_re_adding_same_activity_creates_no_duplicate_favorite(activity_client) -> None:
    client, session_factory = activity_client
    with session_factory() as session:
        session.add(
            BuiltInActivity(
                id="builtin-favorite-02",
                title="Dup favorite",
                level="A2",
                topic="Travel",
                type="Conversation Card",
                prompt="Talk about your last trip.",
            )
        )
        session.commit()

    first = client.post("/favorites", json={"activity_id": "builtin-favorite-02"})
    second = client.post("/favorites", json={"activity_id": "builtin-favorite-02"})

    assert first.status_code == 201
    assert second.status_code == 200
    assert second.json() == {"activity_id": "builtin-favorite-02"}

    with session_factory() as session:
        assert session.query(Favorite).filter_by(activity_id="builtin-favorite-02").count() == 1


def test_favoriting_unknown_activity_and_removing_nonfavorited_activity_are_handled_stably(
    activity_client,
) -> None:
    client, session_factory = activity_client
    with session_factory() as session:
        session.add(
            BuiltInActivity(
                id="builtin-favorite-03",
                title="Keep",
                level="A1",
                topic="Food",
                type="Speaking Challenge",
                prompt="Describe your favorite food.",
            )
        )
        session.add(Favorite(activity_id="builtin-favorite-03"))
        session.commit()

    missing = client.post("/favorites", json={"activity_id": "custom-nope"})
    remove_missing = client.delete("/favorites/custom-nope")
    remove_existing = client.delete("/favorites/builtin-favorite-03")

    assert missing.status_code == 404
    assert remove_missing.status_code == 404
    assert remove_existing.status_code == 200
    assert remove_existing.json() == {"activity_id": "builtin-favorite-03"}

    with session_factory() as session:
        assert session.get(Favorite, "builtin-favorite-03") is None
        assert session.query(Favorite).count() == 0
