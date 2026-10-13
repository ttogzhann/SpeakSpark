from collections import Counter
from pathlib import Path

import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import init_db
from app.database_config import create_sqlite_engine
from app.models import BuiltInActivity, CustomActivity, Favorite
from app.schemas.activity import Activity, ActivityLevel, ActivityTopic, ActivityType


@pytest.fixture
def database(tmp_path: Path) -> tuple[Session, object]:
    engine = create_sqlite_engine(tmp_path / "built-ins.sqlite")
    init_db(bind=engine)
    session = Session(engine)
    yield session, engine
    session.close()
    engine.dispose()


def test_initialization_seeds_exact_curated_builtin_distribution(
    database: tuple[Session, object],
) -> None:
    session, _ = database
    activities = session.scalars(select(BuiltInActivity)).all()

    assert len(activities) == 36
    assert Counter(activity.type for activity in activities) == {
        "Conversation Card": 12,
        "Role-play": 12,
        "Speaking Challenge": 12,
    }
    assert len({activity.id for activity in activities}) == 36
    assert {activity.level for activity in activities} == {"A1", "A2", "B1", "B2"}
    assert {
        activity.topic for activity in activities
    } == {
        "Daily Life",
        "Travel",
        "Food",
        "Education",
        "Work",
        "Hobbies",
        "Technology",
        "Relationships",
    }
    assert all(activity.is_builtin for activity in activities)

    for activity in activities:
        validated = Activity.model_validate(
            {
                "title": activity.title,
                "level": activity.level,
                "topic": activity.topic,
                "type": activity.type,
                "prompt": activity.prompt,
                "follow_up_questions": activity.follow_up_questions,
                "useful_phrases": activity.useful_phrases,
                "roles": activity.roles,
                "instructions": activity.instructions,
            }
        )
        assert validated.title
        assert validated.prompt
        assert validated.level in ActivityLevel.__args__
        assert validated.topic in ActivityTopic.__args__
        assert validated.type in ActivityType.__args__
        if validated.type == "Conversation Card":
            assert "?" in validated.prompt
        elif validated.type == "Role-play":
            assert len(validated.roles) >= 2
            assert all(
                role.participant.strip() and role.objective.strip()
                for role in validated.roles
            )
        else:
            assert any(
                instruction.strip() for instruction in validated.instructions
            ) or len(validated.prompt) >= 30


def test_seed_is_repeatable_without_changing_existing_content_or_other_data(
    database: tuple[Session, object],
) -> None:
    session, engine = database
    before = {
        activity.id: (
            activity.title,
            activity.level,
            activity.topic,
            activity.type,
            activity.prompt,
            activity.follow_up_questions,
            activity.useful_phrases,
            activity.roles,
            activity.instructions,
            activity.is_builtin,
        )
        for activity in session.scalars(select(BuiltInActivity)).all()
    }
    custom = CustomActivity(
        id="custom-preserved",
        title="A tutor activity",
        level="B1",
        topic="Work",
        type="Conversation Card",
        prompt="What makes a team work well?",
    )
    favorite_ids = {
        "builtin-card-daily-life-01",
        "custom-preserved",
    }
    session.add_all([custom, *(Favorite(activity_id=id_) for id_ in favorite_ids)])
    session.commit()

    init_db(bind=engine)
    session.expire_all()
    after_activities = session.scalars(select(BuiltInActivity)).all()
    after = {
        activity.id: (
            activity.title,
            activity.level,
            activity.topic,
            activity.type,
            activity.prompt,
            activity.follow_up_questions,
            activity.useful_phrases,
            activity.roles,
            activity.instructions,
            activity.is_builtin,
        )
        for activity in after_activities
    }

    assert after == before
    assert len(after_activities) == 36
    preserved_custom = session.get(CustomActivity, "custom-preserved")
    assert preserved_custom is not None
    assert (preserved_custom.title, preserved_custom.prompt) == (
        "A tutor activity",
        "What makes a team work well?",
    )
    assert set(session.scalars(select(Favorite.activity_id))) == favorite_ids


def test_builtin_records_cannot_be_updated_or_deleted(
    database: tuple[Session, object],
) -> None:
    session, _ = database
    activity = session.get(BuiltInActivity, "builtin-card-daily-life-01")
    assert activity is not None

    activity.title = "Changed built-in"
    with pytest.raises(IntegrityError, match="Built-in activities are read-only"):
        session.commit()
    session.rollback()

    activity = session.get(BuiltInActivity, "builtin-card-daily-life-01")
    assert activity is not None
    session.delete(activity)
    with pytest.raises(IntegrityError, match="Built-in activities are read-only"):
        session.commit()
    session.rollback()

    assert session.scalar(
        select(BuiltInActivity.id).where(
            BuiltInActivity.id == "builtin-card-daily-life-01"
        )
    )
