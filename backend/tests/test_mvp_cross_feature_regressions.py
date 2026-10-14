"""Cross-feature regressions not covered by the individual endpoint contracts."""

from fastapi.testclient import TestClient

from app.main import app
from test_random_selection import draw, random_client  # noqa: F401


def test_saved_custom_edit_moves_filters_and_selection_pool_then_deletes_cleanly(random_client):
    client = random_client
    activity_id = "custom-b1"
    assert client.post("/favorites", json={"activity_id": activity_id}).status_code == 201
    updated = {
        "title": "Updated saved challenge", "level": "B2", "topic": "Education",
        "type": "Conversation Card", "prompt": "Discuss learning a new skill.",
        "follow_up_questions": ["What would you learn first?"],
    }
    response = client.put(f"/activities/{activity_id}", json=updated)
    assert response.status_code == 200
    expected = response.json()
    # A new API client reads persisted content, not a frontend or response cache.
    reopened = TestClient(app)
    assert reopened.get("/favorites").json() == [expected]
    assert reopened.get(f"/activities/{activity_id}").json() == expected
    assert reopened.get("/activities", params={"level": "B1"}).json() == []
    filters = {"level": "B2", "topic": "Education", "type": "Conversation Cards"}
    assert reopened.get("/activities", params=filters).json() == [expected]
    assert draw(reopened, level="B1") == {"status": "no_matches", "activity": None}
    assert draw(reopened, level="B2", type="Conversation Cards") == {
        "status": "selected", "activity": expected,
    }
    assert reopened.delete(f"/activities/{activity_id}").status_code == 204
    assert TestClient(app).get("/favorites").json() == []
    assert reopened.get(f"/activities/{activity_id}").status_code == 404
    assert draw(reopened, level="B2", type="Conversation Cards") == {
        "status": "no_matches", "activity": None,
    }


def test_invalid_nested_role_edit_is_atomic_for_activity_and_saved_favorite(random_client):
    client = random_client
    activity_id = "custom-b1"
    assert client.post("/favorites", json={"activity_id": activity_id}).status_code == 201
    original = client.get(f"/activities/{activity_id}").json()
    payload = {
        key: value for key, value in original.items() if key not in {"id", "is_builtin"}
    }
    payload.update(title="Must not persist", roles=[{"participant": "Tutor", "objective": "   "}])
    response = client.put(f"/activities/{activity_id}", json=payload)
    assert response.status_code == 422
    assert TestClient(app).get(f"/activities/{activity_id}").json() == original
    assert client.get("/favorites").json() == [original]
    assert draw(client, level="B1") == {"status": "selected", "activity": original}


def test_removing_custom_favorite_keeps_activity_and_unrelated_builtin_favorite(random_client):
    client = random_client
    for activity_id in ("builtin-one", "custom-b1"):
        assert client.post("/favorites", json={"activity_id": activity_id}).status_code == 201
    assert client.post("/favorites", json={"activity_id": "custom-b1"}).status_code == 200
    response = client.delete("/favorites/custom-b1")
    assert response.status_code == 200
    assert response.json() == {"activity_id": "custom-b1"}
    assert [record["id"] for record in TestClient(app).get("/favorites").json()] == ["builtin-one"]
    assert client.get("/activities/custom-b1").status_code == 200
    assert client.delete("/favorites/custom-b1").status_code == 404
