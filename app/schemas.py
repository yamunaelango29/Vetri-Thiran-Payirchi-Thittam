from typing import Literal

from pydantic import BaseModel, Field, field_validator


Goal = Literal["weight loss", "muscle gain", "general wellness", "flexibility"]
Intensity = Literal["low", "medium", "high"]


class UserInput(BaseModel):
    username: str = Field(min_length=2, max_length=100)
    user_id: str = Field(min_length=2, max_length=80, pattern=r"^[A-Za-z0-9_-]+$")
    age: int = Field(ge=13, le=100)
    weight: float = Field(gt=20, le=500)
    goal: Goal
    intensity: Intensity

    @field_validator("username", "user_id")
    @classmethod
    def clean_text(cls, value: str) -> str:
        return value.strip()


class FeedbackRequest(BaseModel):
    user_id: str = Field(min_length=2, max_length=80)
    feedback: str = Field(min_length=3, max_length=1500)

    @field_validator("user_id", "feedback")
    @classmethod
    def clean_text(cls, value: str) -> str:
        return value.strip()


class WorkoutResponse(BaseModel):
    user_id: str
    username: str
    goal: str
    intensity: str
    workout_plan: str
    nutrition_tip: str
    source: Literal["gemini", "demo"]


class FeedbackResponse(BaseModel):
    user_id: str
    updated_plan: str
    nutrition_tip: str
    source: Literal["gemini", "demo"]
