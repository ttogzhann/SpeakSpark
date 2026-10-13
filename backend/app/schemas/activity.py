from typing import Annotated, Literal

from pydantic import BaseModel, Field, StringConstraints

NonEmptyText = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]

ActivityLevel = Literal["A1", "A2", "B1", "B2"]
ActivityTopic = Literal[
    "Daily Life",
    "Travel",
    "Food",
    "Education",
    "Work",
    "Hobbies",
    "Technology",
    "Relationships",
]
ActivityType = Literal["Conversation Card", "Role-play", "Speaking Challenge"]


class ParticipantObjective(BaseModel):
    participant: str
    objective: str


class Activity(BaseModel):
    title: NonEmptyText
    level: ActivityLevel
    topic: ActivityTopic
    type: ActivityType
    prompt: NonEmptyText
    follow_up_questions: list[str] = Field(default_factory=list)
    useful_phrases: list[str] = Field(default_factory=list)
    roles: list[ParticipantObjective] = Field(default_factory=list)
    instructions: list[str] = Field(default_factory=list)


class ActivityResponse(Activity):
    id: str
    is_builtin: bool
