from sqlalchemy import JSON, Boolean, CheckConstraint, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.schemas.activity import ActivityLevel, ActivityTopic, ActivityType


class BuiltInActivity(Base):
    __tablename__ = "built_in_activities"
    __table_args__ = (
        CheckConstraint("is_builtin = 1", name="ck_built_in_activity_is_builtin"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    level: Mapped[ActivityLevel] = mapped_column(String(2), nullable=False)
    topic: Mapped[ActivityTopic] = mapped_column(String(32), nullable=False)
    type: Mapped[ActivityType] = mapped_column(String(32), nullable=False)
    prompt: Mapped[str] = mapped_column(Text, nullable=False)
    follow_up_questions: Mapped[list[str]] = mapped_column(
        JSON, nullable=False, default=list
    )
    useful_phrases: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    roles: Mapped[list[dict[str, str]]] = mapped_column(JSON, nullable=False, default=list)
    instructions: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    is_builtin: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
