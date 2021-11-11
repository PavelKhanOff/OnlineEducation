from typing import Optional

from pydantic import BaseModel


class Homework(BaseModel):
    title: str
    description: str
    lesson_id: int


class HomeworkOut(Homework):
    id: int

    class Config:
        orm_mode = True


class UpdateHomework(BaseModel):
    title: Optional[str]
    description: Optional[str]


class FileOut(BaseModel):
    title: str
    description: Optional[str] = None
    url: Optional[str] = None
    duration: Optional[str] = None
    type: Optional[str] = None

    class Config:
        orm_mode = True
