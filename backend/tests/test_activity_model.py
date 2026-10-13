import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.schemas.activity import Activity, CustomActivityPayload, ParticipantObjective


@pytest.fixture
def required_activity_fields() -> dict[str, str]:
    return {
        "title": "A speaking activity",
        "level": "A1",
        "topic": "Daily Life",
        "type": "Conversation Card",
        "prompt": "Describe your morning routine.",
    }


def test_activity_requires_only_the_shared_core_fields(
    required_activity_fields: dict[str, str],
) -> None:
    activity = Activity(**required_activity_fields)

    assert activity.model_dump() == {
        **required_activity_fields,
        "follow_up_questions": [],
        "useful_phrases": [],
        "roles": [],
        "instructions": [],
    }


@pytest.mark.parametrize(
    "activity_type", ["Conversation Card", "Role-play", "Speaking Challenge"]
)
def test_each_activity_type_accepts_minimal_payload(
    required_activity_fields: dict[str, str], activity_type: str
) -> None:
    activity = Activity(**{**required_activity_fields, "type": activity_type})

    assert activity.type == activity_type
    assert activity.roles == []


def test_activity_accepts_explicit_empty_optional_lists(
    required_activity_fields: dict[str, str],
) -> None:
    activity = Activity(
        **{
            **required_activity_fields,
            "follow_up_questions": [],
            "useful_phrases": [],
            "roles": [],
            "instructions": [],
        }
    )

    assert activity.follow_up_questions == []
    assert activity.useful_phrases == []
    assert activity.roles == []
    assert activity.instructions == []


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("title", ""),
        ("title", "   "),
        ("level", "C1"),
        ("topic", "Sports"),
        ("type", "Debate"),
        ("prompt", ""),
        ("prompt", "   "),
    ],
)
def test_activity_rejects_invalid_required_field_values(
    required_activity_fields: dict[str, str], field: str, value: str
) -> None:
    with pytest.raises(ValidationError):
        Activity(**{**required_activity_fields, field: value})


@pytest.mark.parametrize(
    ("field", "values"),
    [
        ("level", ["A1", "A2", "B1", "B2"]),
        (
            "topic",
            [
                "Daily Life",
                "Travel",
                "Food",
                "Education",
                "Work",
                "Hobbies",
                "Technology",
                "Relationships",
            ],
        ),
        ("type", ["Conversation Card", "Role-play", "Speaking Challenge"]),
    ],
)
def test_activity_accepts_every_approved_value(
    required_activity_fields: dict[str, str], field: str, values: list[str]
) -> None:
    for value in values:
        activity = Activity(**{**required_activity_fields, field: value})
        assert getattr(activity, field) == value


@pytest.mark.parametrize(
    ("activity_type", "optional_fields"),
    [
        ("Conversation Card", {"follow_up_questions": ["Why?"]}),
        (
            "Role-play",
            {
                "roles": [
                    {"participant": "Customer", "objective": "Order a meal."},
                    {"participant": "Server", "objective": "Recommend a dish."},
                ],
                "useful_phrases": ["Could I have...?"],
            },
        ),
        (
            "Speaking Challenge",
            {"instructions": ["Speak for one minute."], "useful_phrases": ["First..."]},
        ),
    ],
)
def test_activity_types_share_required_fields_and_optional_guidance(
    required_activity_fields: dict[str, str],
    activity_type: str,
    optional_fields: dict[str, object],
) -> None:
    activity = Activity(
        **{**required_activity_fields, "type": activity_type, **optional_fields}
    )

    assert activity.type == activity_type
    for field, value in optional_fields.items():
        assert activity.model_dump()[field] == value


def test_roles_use_participant_and_objective_pairs() -> None:
    role = ParticipantObjective.model_validate(
        {"participant": "Student", "objective": "Ask for directions."}
    )

    assert role.model_dump() == {
        "participant": "Student",
        "objective": "Ask for directions.",
    }


def test_activity_declares_exact_required_and_optional_fields() -> None:
    required_fields = {"title", "level", "topic", "type", "prompt"}
    optional_fields = {
        "follow_up_questions",
        "useful_phrases",
        "roles",
        "instructions",
    }

    assert set(Activity.model_fields) == required_fields | optional_fields
    assert {
        name for name, field in Activity.model_fields.items() if field.is_required()
    } == required_fields


def test_activity_enforces_title_length_boundaries(
    required_activity_fields: dict[str, str],
) -> None:
    assert Activity(**{**required_activity_fields, "title": "T" * 120}).title == "T" * 120

    with pytest.raises(ValidationError):
        Activity(**{**required_activity_fields, "title": "T" * 121})


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("title", None),
        ("title", 42),
        ("prompt", None),
        ("prompt", 42),
        ("follow_up_questions", None),
        ("follow_up_questions", "Why?"),
        ("follow_up_questions", ["  "]),
        ("useful_phrases", [None]),
        ("instructions", [42]),
        ("roles", None),
        ("roles", {"participant": "Student", "objective": "Ask a question."}),
        ("roles", [{"participant": "  ", "objective": "Ask a question."}]),
        ("roles", [{"participant": "Student", "objective": "Ask a question.", "extra": "x"}]),
    ],
)
def test_activity_rejects_malformed_payload_values(
    required_activity_fields: dict[str, str], field: str, value: object
) -> None:
    with pytest.raises(ValidationError):
        Activity(**{**required_activity_fields, field: value})


def test_activity_rejects_unrecognized_payload_fields(
    required_activity_fields: dict[str, str],
) -> None:
    with pytest.raises(ValidationError):
        Activity(**{**required_activity_fields, "promt": "A typo."})


def test_fastapi_request_body_validation_returns_structured_422(
    required_activity_fields: dict[str, str],
) -> None:
    validation_app = FastAPI()

    @validation_app.post("/validation-only")
    def validate_payload(payload: CustomActivityPayload) -> CustomActivityPayload:
        return payload

    client = TestClient(validation_app)
    valid_response = client.post("/validation-only", json=required_activity_fields)
    invalid_response = client.post(
        "/validation-only", json={**required_activity_fields, "title": " "}
    )

    assert valid_response.status_code == 200
    assert invalid_response.status_code == 422
    errors = invalid_response.json()["detail"]
    assert any(error["loc"] == ["body", "title"] for error in errors)
