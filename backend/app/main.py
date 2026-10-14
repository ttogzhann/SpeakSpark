from typing import Annotated, Literal
from uuid import uuid4

from fastapi import Depends, FastAPI, HTTPException, Path, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import BuiltInActivity, CustomActivity, Favorite
from app.random_selection import RandomActivityResponse, RandomActivitySelector
from app.schemas.activity import (
    ActivityLevel,
    ActivityResponse,
    ActivityTopic,
    ActivityType,
    CustomActivityPayload,
)


class FavoritePayload(BaseModel):
    activity_id: str

app = FastAPI(title="SpeakSpark API")
app.state.random_selector = RandomActivitySelector()


def get_random_selector() -> RandomActivitySelector:
    return app.state.random_selector

ACTIVITY_ID_PATTERN = (
    r"^(?:builtin-[a-z0-9]+(?:-[a-z0-9]+)*|"
    r"custom-[a-z0-9]+(?:-[a-z0-9]+)*|"
    r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-"
    r"[0-9a-fA-F]{4}-[0-9a-fA-F]{12})$"
)

ActivityFilterCategory = Literal[
    "Conversation Cards", "Role-play Scenarios", "Speaking Challenges"
]
ACTIVITY_FILTER_TYPE_ALIASES: dict[str, ActivityType] = {
    "Conversation Cards": "Conversation Card",
    "Role-play Scenarios": "Role-play",
    "Speaking Challenges": "Speaking Challenge",
}


@app.on_event("startup")
def startup_event() -> None:
    from app.database import init_db

    init_db()


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/random-activities/next", response_model=RandomActivityResponse)
def next_random_activity(
    level: ActivityLevel,
    activity_type: ActivityFilterCategory | None = Query(default=None, alias="type"),
    db: Session = Depends(get_db),
    selector: RandomActivitySelector = Depends(get_random_selector),
) -> RandomActivityResponse:
    normalized_type = (
        ACTIVITY_FILTER_TYPE_ALIASES[activity_type] if activity_type is not None else None
    )
    return selector.next(db, level, normalized_type)


def _activity_response(
    activity: BuiltInActivity | CustomActivity, is_builtin: bool
) -> ActivityResponse:
    return ActivityResponse(
        id=activity.id,
        title=activity.title,
        level=activity.level,
        topic=activity.topic,
        type=activity.type,
        prompt=activity.prompt,
        follow_up_questions=activity.follow_up_questions or [],
        useful_phrases=activity.useful_phrases or [],
        roles=activity.roles or [],
        instructions=activity.instructions or [],
        is_builtin=is_builtin,
    )


@app.get("/activities", response_model=list[ActivityResponse])
def list_activities(
    level: ActivityLevel | None = None,
    topic: ActivityTopic | None = None,
    activity_type: ActivityFilterCategory | None = Query(default=None, alias="type"),
    db: Session = Depends(get_db),
) -> list[ActivityResponse]:
    normalized_type = (
        ACTIVITY_FILTER_TYPE_ALIASES[activity_type]
        if activity_type is not None
        else None
    )
    built_in_filters = []
    custom_filters = []
    if level is not None:
        built_in_filters.append(BuiltInActivity.level == level)
        custom_filters.append(CustomActivity.level == level)
    if topic is not None:
        built_in_filters.append(BuiltInActivity.topic == topic)
        custom_filters.append(CustomActivity.topic == topic)
    if normalized_type is not None:
        built_in_filters.append(BuiltInActivity.type == normalized_type)
        custom_filters.append(CustomActivity.type == normalized_type)

    built_in_activities = db.scalars(
        select(BuiltInActivity).where(*built_in_filters).order_by(BuiltInActivity.id)
    ).all()
    custom_activities = db.scalars(
        select(CustomActivity).where(*custom_filters).order_by(CustomActivity.id)
    ).all()

    activities = [
        (activity, True) for activity in built_in_activities
    ] + [(activity, False) for activity in custom_activities]

    return [
        _activity_response(activity, is_builtin)
        for activity, is_builtin in activities
    ]


@app.get("/activities/{activity_id}", response_model=ActivityResponse)
def get_activity(
    activity_id: Annotated[str, Path(pattern=ACTIVITY_ID_PATTERN)],
    db: Session = Depends(get_db),
) -> ActivityResponse:
    activity = db.get(BuiltInActivity, activity_id)
    is_builtin = activity is not None

    if activity is None:
        activity = db.get(CustomActivity, activity_id)
        is_builtin = False

    if activity is None:
        raise HTTPException(status_code=404, detail="Activity not found")

    return _activity_response(activity, is_builtin)


@app.post("/activities", response_model=ActivityResponse, status_code=201)
def create_activity(
    payload: CustomActivityPayload,
    db: Session = Depends(get_db),
) -> ActivityResponse:
    custom_activity = CustomActivity(
        id=str(uuid4()),
        title=payload.title,
        level=payload.level,
        topic=payload.topic,
        type=payload.type,
        prompt=payload.prompt,
        follow_up_questions=list(payload.follow_up_questions),
        useful_phrases=list(payload.useful_phrases),
        roles=[role.model_dump() for role in payload.roles],
        instructions=list(payload.instructions),
    )
    db.add(custom_activity)
    db.commit()
    db.refresh(custom_activity)
    return _activity_response(custom_activity, is_builtin=False)


@app.put("/activities/{activity_id}", response_model=ActivityResponse)
def update_activity(
    activity_id: str,
    payload: CustomActivityPayload,
    db: Session = Depends(get_db),
) -> ActivityResponse:
    activity = db.get(CustomActivity, activity_id)
    if activity is None:
        if db.get(BuiltInActivity, activity_id) is not None:
            raise HTTPException(status_code=400, detail="Built-in activities are read-only")
        raise HTTPException(status_code=404, detail="Activity not found")

    activity.title = payload.title
    activity.level = payload.level
    activity.topic = payload.topic
    activity.type = payload.type
    activity.prompt = payload.prompt
    activity.follow_up_questions = list(payload.follow_up_questions)
    activity.useful_phrases = list(payload.useful_phrases)
    activity.roles = [role.model_dump() for role in payload.roles]
    activity.instructions = list(payload.instructions)
    db.add(activity)
    db.commit()
    db.refresh(activity)
    return _activity_response(activity, is_builtin=False)


@app.delete("/activities/{activity_id}", status_code=204)
def delete_activity(
    activity_id: Annotated[str, Path(pattern=ACTIVITY_ID_PATTERN)],
    db: Session = Depends(get_db),
) -> None:
    activity = db.get(CustomActivity, activity_id)
    if activity is None:
        if db.get(BuiltInActivity, activity_id) is not None:
            raise HTTPException(status_code=400, detail="Built-in activities are read-only")
        raise HTTPException(status_code=404, detail="Activity not found")

    favorite_matches = db.scalars(
        select(Favorite).where(Favorite.activity_id == activity_id)
    ).all()
    for favorite in favorite_matches:
        db.delete(favorite)

    db.delete(activity)
    db.commit()


@app.get("/favorites", response_model=list[ActivityResponse])
def list_favorites(db: Session = Depends(get_db)) -> list[ActivityResponse]:
    built_in_activities = db.scalars(
        select(BuiltInActivity)
        .join(Favorite, Favorite.activity_id == BuiltInActivity.id)
        .order_by(BuiltInActivity.id)
    ).all()
    custom_activities = db.scalars(
        select(CustomActivity)
        .join(Favorite, Favorite.activity_id == CustomActivity.id)
        .order_by(CustomActivity.id)
    ).all()

    return [
        _activity_response(activity, is_builtin=True)
        for activity in built_in_activities
    ] + [
        _activity_response(activity, is_builtin=False)
        for activity in custom_activities
    ]


@app.post("/favorites", response_model=dict[str, str])
def add_favorite(
    payload: FavoritePayload,
    db: Session = Depends(get_db),
) -> dict[str, str]:
    activity_id = payload.activity_id
    if not db.get(BuiltInActivity, activity_id) and not db.get(CustomActivity, activity_id):
        raise HTTPException(status_code=404, detail="Activity not found")

    existing = db.get(Favorite, activity_id)
    if existing is not None:
        return JSONResponse(status_code=200, content={"activity_id": activity_id})

    db.add(Favorite(activity_id=activity_id))
    db.commit()
    return JSONResponse(status_code=201, content={"activity_id": activity_id})


@app.delete("/favorites/{activity_id}", response_model=dict[str, str])
def remove_favorite(
    activity_id: Annotated[str, Path(pattern=ACTIVITY_ID_PATTERN)],
    db: Session = Depends(get_db),
) -> dict[str, str]:
    favorite = db.get(Favorite, activity_id)
    if favorite is None:
        raise HTTPException(status_code=404, detail="Favorite not found")

    db.delete(favorite)
    db.commit()
    return {"activity_id": activity_id}
