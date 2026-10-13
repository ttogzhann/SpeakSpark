from pathlib import Path

import pytest
from sqlalchemy import inspect, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import Base, init_db
from app.database_config import create_sqlite_engine
from app.models import CustomActivity, Favorite


@pytest.fixture
def session(tmp_path: Path) -> Session:
    engine = create_sqlite_engine(tmp_path / "models.sqlite")
    init_db(bind=engine)
    with Session(engine) as test_session:
        yield test_session
    engine.dispose()


def make_custom_activity(**overrides: object) -> CustomActivity:
    activity_fields: dict[str, object] = {
        "title": "At the café",
        "level": "A2",
        "topic": "Food",
        "type": "Role-play",
        "prompt": "Order a drink and ask about the menu.",
    }
    activity_fields.update(overrides)
    return CustomActivity(**activity_fields)


def test_models_are_registered_and_schema_initializes_in_clean_sqlite(
    session: Session,
) -> None:
    assert set(Base.metadata.tables) >= {"custom_activities", "favorites"}
    assert set(inspect(session.get_bind()).get_table_names()) == set(
        Base.metadata.tables
    )


def test_custom_activity_persists_shared_fields_and_optional_guidance(
    session: Session,
) -> None:
    activity = make_custom_activity(
        follow_up_questions=["What would you recommend?"],
        useful_phrases=["Could I have...?", "How much is...?"],
        roles=[
            {"participant": "Customer", "objective": "Order a drink."},
            {"participant": "Server", "objective": "Recommend a drink."},
        ],
        instructions=["Take turns asking and answering."],
    )
    session.add(activity)
    session.commit()

    reloaded = session.get(CustomActivity, activity.id)
    assert reloaded is not None
    assert reloaded.id == activity.id
    assert {
        "title": reloaded.title,
        "level": reloaded.level,
        "topic": reloaded.topic,
        "type": reloaded.type,
        "prompt": reloaded.prompt,
        "follow_up_questions": reloaded.follow_up_questions,
        "useful_phrases": reloaded.useful_phrases,
        "roles": reloaded.roles,
        "instructions": reloaded.instructions,
    } == {
        "title": "At the café",
        "level": "A2",
        "topic": "Food",
        "type": "Role-play",
        "prompt": "Order a drink and ask about the menu.",
        "follow_up_questions": ["What would you recommend?"],
        "useful_phrases": ["Could I have...?", "How much is...?"],
        "roles": [
            {"participant": "Customer", "objective": "Order a drink."},
            {"participant": "Server", "objective": "Recommend a drink."},
        ],
        "instructions": ["Take turns asking and answering."],
    }


def test_custom_activity_can_leave_optional_guidance_absent(session: Session) -> None:
    activity = make_custom_activity()
    session.add(activity)
    session.commit()

    reloaded = session.get(CustomActivity, activity.id)
    assert reloaded is not None
    assert reloaded.follow_up_questions is None
    assert reloaded.useful_phrases is None
    assert reloaded.roles is None
    assert reloaded.instructions is None


def test_favorite_persists_built_in_and_custom_activity_ids(session: Session) -> None:
    custom_activity = make_custom_activity()
    session.add_all(
        [
            custom_activity,
            Favorite(activity_id="builtin-airport-01"),
        ]
    )
    session.flush()
    session.add(Favorite(activity_id=custom_activity.id))
    session.commit()

    saved_ids = set(session.scalars(select(Favorite.activity_id)))
    assert saved_ids == {"builtin-airport-01", custom_activity.id}
    assert session.get(Favorite, custom_activity.id).custom_activity == custom_activity
    assert session.get(Favorite, "builtin-airport-01").custom_activity is None


def test_favorite_activity_id_is_unique(session: Session) -> None:
    session.add(Favorite(activity_id="builtin-airport-01"))
    session.commit()

    session.add(Favorite(activity_id="builtin-airport-01"))
    with pytest.raises(IntegrityError):
        session.commit()
    session.rollback()

    assert session.scalars(select(Favorite.activity_id)).all() == [
        "builtin-airport-01"
    ]


def test_deleting_custom_activity_only_deletes_its_favorites(
    session: Session,
) -> None:
    deleted_activity = make_custom_activity(id="custom-to-delete")
    remaining_activity = make_custom_activity(id="custom-to-keep", title="Another")
    built_in_favorite = Favorite(activity_id="builtin-airport-01")
    deleted_favorite = Favorite(activity_id=deleted_activity.id)
    remaining_favorite = Favorite(activity_id=remaining_activity.id)
    deleted_activity.favorites.append(deleted_favorite)
    remaining_activity.favorites.append(remaining_favorite)
    session.add_all(
        [deleted_activity, remaining_activity, built_in_favorite]
    )
    session.commit()

    session.delete(deleted_activity)
    session.commit()

    assert session.get(Favorite, deleted_activity.id) is None
    assert session.get(Favorite, remaining_activity.id) is not None
    assert session.get(Favorite, "builtin-airport-01") is not None
