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


class Lesson(BaseModel):
    title: str
    description: str
    estimated_time: str
    course_id: int


class LessonOut(Lesson):
    id: int

    class Config:
        orm_mode = True


class File(BaseModel):
    title: str
    description: Optional[str] = None
    url: Optional[str] = None
    duration: Optional[str] = None
    type: Optional[str] = None
    course_id: Optional[int] = None
    lesson_id: Optional[int] = None
    homework_id: Optional[int] = None


class FileOut(BaseModel):
    title: str
    description: Optional[str] = None
    url: Optional[str] = None
    duration: Optional[str] = None
    type: Optional[str] = None

    class Config:
        orm_mode = True


class FileToLesson(BaseModel):
    title: str
    description: Optional[str] = None
    url: Optional[str] = None
    duration: Optional[int] = None
    type: Optional[str] = None


class AddTag(BaseModel):
    tag_id: int
    lesson_id: int


class UpdateLesson(BaseModel):
    title: str
    description: str
    estimated_time: str
