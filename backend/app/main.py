from fastapi import Depends, FastAPI
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import BuiltInActivity, CustomActivity
from app.schemas.activity import ActivityResponse

app = FastAPI(title="SpeakSpark API")


@app.on_event("startup")
def startup_event() -> None:
    from app.database import init_db

    init_db()


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


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
        ActivityResponse(
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
        for activity, is_builtin in activities
    ]
