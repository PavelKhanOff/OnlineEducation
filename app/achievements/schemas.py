import datetime
from typing import Any, List, Optional, Union

from fastapi_users import FastAPIUsers, models
from pydantic import (
    UUID4,
    AnyUrl,
    BaseModel,
    EmailStr,
    Field,
    root_validator,
    validator,
)


class Achievement(BaseModel):
    title: str
    description: str


class UpdateAchievement(BaseModel):
    avatar: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None


class AchievementOut(Achievement):
    id: int
    avatar: Any

    class Config:
        orm_mode = True


class UserAchievement(BaseModel):
    achievements_id: int
