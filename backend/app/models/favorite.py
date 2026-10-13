from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, foreign, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.custom_activity import CustomActivity


class Favorite(Base):
    __tablename__ = "favorites"

    activity_id: Mapped[str] = mapped_column(String, primary_key=True)

    custom_activity: Mapped["CustomActivity | None"] = relationship(
        "CustomActivity",
        primaryjoin="foreign(Favorite.activity_id) == CustomActivity.id",
        back_populates="favorites",
    )
