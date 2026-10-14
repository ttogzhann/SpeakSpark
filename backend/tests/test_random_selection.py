from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.database_config import create_sqlite_engine
from app.main import app, get_random_selector
from app.models import BuiltInActivity, CustomActivity
from app.random_selection import RandomActivitySelector


@pytest.fixture
def random_client(tmp_path: Path):
    engine = create_sqlite_engine(tmp_path / "random.sqlite")
    Base.metadata.create_all(engine)
    sessions = sessionmaker(bind=engine)
    with sessions() as db:
        for model, activity_id, level, activity_type in (
            (BuiltInActivity, "builtin-one", "A1", "Conversation Card"),
            (BuiltInActivity, "builtin-two", "A1", "Conversation Card"),
            (CustomActivity, "custom-three", "A1", "Conversation Card"),
            (CustomActivity, "custom-role", "A1", "Role-play"),
            (BuiltInActivity, "builtin-a2", "A2", "Speaking Challenge"),
            (CustomActivity, "custom-b1", "B1", "Role-play"),
            (CustomActivity, "custom-b2", "B2", "Speaking Challenge"),
        ):
            db.add(model(id=activity_id, title=activity_id, level=level,
                         type=activity_type, topic="Travel", prompt="Discuss travel.",
                         instructions=["Take turns."]))
        db.commit()

    def test_db():
        with sessions() as db:
            yield db

    selector = RandomActivitySelector()
    old_overrides = app.dependency_overrides.copy()
    app.dependency_overrides[get_db] = test_db
    app.dependency_overrides[get_random_selector] = lambda: selector
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()
        app.dependency_overrides.update(old_overrides)
        engine.dispose()


def draw(client, **params):
    response = client.post("/random-activities/next", params=params)
    assert response.status_code == 200
    return response.json()


@pytest.mark.parametrize("params", [{}, {"level": "C1"}, {"level": ""},
    {"level": "A1", "type": "Conversation Card"}, {"level": "A1", "type": "unknown"}])
def test_invalid_filters_do_not_advance_cycle(random_client, params):
    first = draw(random_client, level="A1")
    assert random_client.post("/random-activities/next", params=params).status_code == 422
    rest = [draw(random_client, level="A1") for _ in range(3)]
    assert len({item["activity"]["id"] for item in [first, *rest]}) == 4
    assert draw(random_client, level="A1") == {"status": "exhausted", "activity": None}


@pytest.mark.parametrize("level", ["A1", "A2", "B1", "B2"])
def test_all_supported_levels_and_complete_response(random_client, level):
    result = draw(random_client, level=level)
    assert result["status"] == "selected"
    activity = result["activity"]
    assert activity["level"] == level
    assert activity == random_client.get(f"/activities/{activity['id']}").json()
    assert activity["instructions"] == ["Take turns."]


@pytest.mark.parametrize("activity_type,level,count", [
    ("Conversation Cards", "A1", 3), ("Role-play Scenarios", "A1", 1),
    ("Speaking Challenges", "A2", 1),
])
def test_filtered_unique_cycle_exhaustion_and_restart(random_client, activity_type, level, count):
    params = {"level": level, "type": activity_type}
    expected = random_client.get("/activities", params=params).json()
    records = [draw(random_client, **params)["activity"] for _ in range(count)]
    assert {record["id"] for record in records} == {record["id"] for record in expected}
    assert draw(random_client, **params) == {"status": "exhausted", "activity": None}
    assert draw(random_client, **params)["activity"]["id"] in {r["id"] for r in expected}


def test_filter_changes_always_start_fresh_cycle(random_client, monkeypatch):
    monkeypatch.setattr("app.random_selection.random.choice", lambda remaining: remaining[0])
    first = draw(random_client, level="A1")["activity"]["id"]
    assert draw(random_client, level="A1")["activity"]["id"] != first
    draw(random_client, level="A2")
    assert draw(random_client, level="A1")["activity"]["id"] == first
    assert draw(random_client, level="A1", type="Conversation Cards")["activity"]["id"] == first
    assert draw(random_client, level="A1")["activity"]["id"] == first
    assert draw(random_client, level="A1", type="Role-play Scenarios")["activity"]["id"] == "custom-role"


def test_uniform_choice_receives_combined_remaining_records(random_client, monkeypatch):
    pools = []

    def choose(remaining):
        pools.append([(record.id, builtin) for record, builtin in remaining])
        return remaining[-1]

    monkeypatch.setattr("app.random_selection.random.choice", choose)
    selected = [draw(random_client, level="A1", type="Conversation Cards")["activity"]
                for _ in range(3)]
    assert pools == [
        [("builtin-one", True), ("builtin-two", True), ("custom-three", False)],
        [("builtin-one", True), ("builtin-two", True)],
        [("builtin-one", True)],
    ]
    assert [record["is_builtin"] for record in selected] == [False, True, True]


def test_empty_pool_uses_reserved_response(random_client):
    assert draw(random_client, level="B2", type="Conversation Cards") == {
        "status": "no_matches", "activity": None,
    }
