from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Path
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import BuiltInActivity, CustomActivity
from app.schemas.activity import ActivityResponse

app = FastAPI(title="SpeakSpark API")

ACTIVITY_ID_PATTERN = (
    r"^(?:builtin-[a-z0-9]+(?:-[a-z0-9]+)*|"
    r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-"
    r"[0-9a-fA-F]{4}-[0-9a-fA-F]{12})$"
)


@app.on_event("startup")
def startup_event() -> None:
    from app.database import init_db

    init_db()


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


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
def list_activities(db: Session = Depends(get_db)) -> list[ActivityResponse]:
    built_in_activities = db.scalars(
        select(BuiltInActivity).order_by(BuiltInActivity.id)
    ).all()
    custom_activities = db.scalars(
        select(CustomActivity).order_by(CustomActivity.id)
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
