"""One process-local selection cycle for the single tutor workspace."""

import random
from threading import Lock
from typing import Literal

from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import BuiltInActivity, CustomActivity
from app.schemas.activity import ActivityLevel, ActivityResponse, ActivityType


class RandomActivityResponse(BaseModel):
    status: Literal["selected", "exhausted", "no_matches"]
    activity: ActivityResponse | None


class RandomActivitySelector:
    def __init__(self) -> None:
        self._lock = Lock()
        self._filters: tuple[ActivityLevel, ActivityType | None] | None = None
        self._seen: set[tuple[bool, str]] = set()

    def next(
        self, db: Session, level: ActivityLevel, activity_type: ActivityType | None
    ) -> RandomActivityResponse:
        # Serialize the entire read/draw/history transition across API workers' threads.
        with self._lock:
            filters = (level, activity_type)
            if filters != self._filters:
                self._filters = filters
                self._seen.clear()

            candidates = []
            for model, is_builtin in ((BuiltInActivity, True), (CustomActivity, False)):
                query = select(model).where(model.level == level).order_by(model.id)
                if activity_type is not None:
                    query = query.where(model.type == activity_type)
                candidates.extend((record, is_builtin) for record in db.scalars(query))

            if not candidates:
                self._seen.clear()
                return RandomActivityResponse(status="no_matches", activity=None)

            remaining = [
                candidate for candidate in candidates
                if (candidate[1], candidate[0].id) not in self._seen
            ]
            if not remaining:
                self._seen.clear()
                return RandomActivityResponse(status="exhausted", activity=None)

            # A single uniform choice across records gives both sources equal weight.
            record, is_builtin = random.choice(remaining)
            activity = ActivityResponse(
                id=record.id, is_builtin=is_builtin, title=record.title,
                level=record.level, topic=record.topic, type=record.type,
                prompt=record.prompt,
                follow_up_questions=record.follow_up_questions or [],
                useful_phrases=record.useful_phrases or [],
                roles=record.roles or [], instructions=record.instructions or [],
            )
            self._seen.add((is_builtin, record.id))
            return RandomActivityResponse(status="selected", activity=activity)
