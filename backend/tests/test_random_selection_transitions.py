"""Regression coverage for transitions around the existing random selector."""

import pytest
from sqlalchemy import select

from app.database import get_db
from app.main import app
from app.models import BuiltInActivity, CustomActivity, Favorite
from test_random_selection import draw, random_client  # noqa: F401


def test_empty_pool_observes_creation_and_deletion_without_restart(random_client):
    params = {"level": "B2", "type": "Conversation Cards"}
    empty = {"status": "no_matches", "activity": None}
    assert draw(random_client, **params) == empty
    assert draw(random_client, **params) == empty
    response = random_client.post("/activities", json={
        "title": "New matching card", "level": "B2", "topic": "Work",
        "type": "Conversation Card", "prompt": "Discuss your ideal job.",
    })
    assert response.status_code == 201
    activity = response.json()
    assert draw(random_client, **params) == {"status": "selected", "activity": activity}
    assert random_client.delete(f"/activities/{activity['id']}").status_code == 204
    assert draw(random_client, **params) == empty
    assert draw(random_client, **params) == empty


@pytest.mark.parametrize("params,count", [
    ({"level": "B1", "type": "Role-play Scenarios"}, 1),
    ({"level": "A1"}, 4),
])
def test_repeated_complete_cycles_remain_distinct(random_client, params, count):
    expected = {record["id"] for record in random_client.get("/activities", params=params).json()}
    for _ in range(3):
        results = [draw(random_client, **params) for _ in range(count)]
        assert all(result["status"] == "selected" for result in results)
        assert {result["activity"]["id"] for result in results} == expected
        assert len({result["activity"]["id"] for result in results}) == count
        assert draw(random_client, **params) == {"status": "exhausted", "activity": None}


def test_empty_filter_round_trip_and_removing_type_start_fresh(random_client, monkeypatch):
    monkeypatch.setattr("app.random_selection.random.choice", lambda pool: pool[0])
    first = draw(random_client, level="A1", type="Conversation Cards")["activity"]
    assert draw(random_client, level="A1", type="Speaking Challenges") == {
        "status": "no_matches", "activity": None,
    }
    assert draw(random_client, level="A1", type="Conversation Cards")["activity"] == first
    # Removing type resets the previously consumed first card and includes role-play.
    results = [draw(random_client, level="A1")["activity"] for _ in range(4)]
    assert results[0] == first
    assert {record["type"] for record in results} == {"Conversation Card", "Role-play"}
    assert {record["id"] for record in results} == {
        record["id"] for record in random_client.get("/activities", params={"level": "A1"}).json()
    }


@pytest.mark.parametrize("invalid", [
    {}, {"level": "C1"}, {"level": "A2", "type": "invalid"},
])
def test_invalid_requests_preserve_exhaustion_boundary(random_client, invalid):
    # A different valid level with an invalid type must never reset B1 history.
    first = draw(random_client, level="B1")
    assert first["status"] == "selected"
    assert random_client.post("/random-activities/next", params=invalid).status_code == 422
    assert draw(random_client, level="B1") == {"status": "exhausted", "activity": None}
    assert random_client.post("/random-activities/next", params=invalid).status_code == 422
    assert draw(random_client, level="B1") == first


def test_invalid_different_level_preserves_partially_consumed_cycle(random_client):
    first = draw(random_client, level="A1")
    response = random_client.post("/random-activities/next", params={"level": "A2", "type": "invalid"})
    assert response.status_code == 422
    remaining = [draw(random_client, level="A1") for _ in range(3)]
    assert len({result["activity"]["id"] for result in [first, *remaining]}) == 4
    assert draw(random_client, level="A1") == {"status": "exhausted", "activity": None}


def database_snapshot():
    dependency = app.dependency_overrides[get_db]()
    db = next(dependency)
    try:
        return {
            model.__tablename__: [
                {column.name: getattr(record, column.name) for column in model.__table__.columns}
                for record in db.scalars(select(model).order_by(model.__table__.primary_key.columns))
            ]
            for model in (BuiltInActivity, CustomActivity, Favorite)
        }
    finally:
        dependency.close()


def test_every_transition_preserves_activities_and_favorites(random_client):
    for activity_id in ("builtin-one", "custom-b1"):
        assert random_client.post("/favorites", json={"activity_id": activity_id}).status_code == 201
    before = database_snapshot()
    assert draw(random_client, level="B1")["status"] == "selected"
    assert database_snapshot() == before
    assert draw(random_client, level="B1")["status"] == "exhausted"
    assert database_snapshot() == before
    assert draw(random_client, level="B1")["status"] == "selected"
    assert database_snapshot() == before
    assert draw(random_client, level="B2", type="Conversation Cards")["status"] == "no_matches"
    assert database_snapshot() == before
    assert random_client.post("/random-activities/next", params={"level": "A2", "type": "invalid"}).status_code == 422
    assert database_snapshot() == before
