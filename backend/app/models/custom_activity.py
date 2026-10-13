from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.schemas.activity import ActivityLevel, ActivityTopic, ActivityType

if TYPE_CHECKING:
    from app.models.favorite import Favorite


class CustomActivity(Base):
    __tablename__ = "custom_activities"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid4())
    )
    title: Mapped[str] = mapped_column(String, nullable=False)
    level: Mapped[ActivityLevel] = mapped_column(String(2), nullable=False)
    topic: Mapped[ActivityTopic] = mapped_column(String(32), nullable=False)
    type: Mapped[ActivityType] = mapped_column(String(32), nullable=False)
    prompt: Mapped[str] = mapped_column(Text, nullable=False)
    follow_up_questions: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)
    useful_phrases: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)
    roles: Mapped[list[dict[str, str]] | None] = mapped_column(JSON, nullable=True)
    instructions: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)

    favorites: Mapped[list["Favorite"]] = relationship(
        "Favorite",
        primaryjoin="CustomActivity.id == foreign(Favorite.activity_id)",
        back_populates="custom_activity",
        cascade="all, delete-orphan",
    )
