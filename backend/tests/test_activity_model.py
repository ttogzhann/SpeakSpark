import pytest
from pydantic import ValidationError

from app.schemas.activity import Activity, ParticipantObjective


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
