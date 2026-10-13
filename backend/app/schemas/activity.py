from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, StringConstraints

NonEmptyText = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
ActivityTitle = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=1, max_length=120)
]

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
    model_config = ConfigDict(extra="forbid")

    participant: NonEmptyText
    objective: NonEmptyText


class CustomActivityPayload(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: ActivityTitle
    level: ActivityLevel
    topic: ActivityTopic
    type: ActivityType
    prompt: NonEmptyText
    follow_up_questions: list[NonEmptyText] = Field(default_factory=list)
    useful_phrases: list[NonEmptyText] = Field(default_factory=list)
    roles: list[ParticipantObjective] = Field(default_factory=list)
    instructions: list[NonEmptyText] = Field(default_factory=list)


class Activity(CustomActivityPayload):
    pass


class ActivityResponse(Activity):
    id: str
    is_builtin: bool
