from typing import Optional

from pydantic import BaseModel


class FileBase(BaseModel):
    title: str
    description: Optional[str] = None
    url: Optional[str] = None
    duration: Optional[int] = None
    type: Optional[str] = None
    key: Optional[str] = None


class File(FileBase):
    course_id: Optional[int] = None
    content_id: Optional[int] = None
    homework_id: Optional[int] = None


class Content(FileBase):
    content_id: Optional[int] = None
    user_id: Optional[str] = None


class Avatar(BaseModel):
    url: Optional[str] = None
    title: str
    key: Optional[str] = None
    user_id: Optional[str] = None
    course_id: Optional[int] = None
    achievement_id: Optional[int] = None


class AvatarOut(BaseModel):
    id: int
    url: Optional[str] = None
    title: str
    key: Optional[str] = None

    class Config:
        orm_mode = True


class FileToCourse(BaseModel):
    title: str
    description: Optional[str] = None
    url: Optional[str] = None
    duration: Optional[int] = None
    type: Optional[str] = None
    course_id: Optional[int] = None
    key: Optional[str] = None


class FileToHomework(BaseModel):
    title: str
    description: Optional[str] = None
    url: Optional[str] = None
    duration: Optional[int] = None
    type: Optional[str] = None
    homework_id: Optional[int] = None
    key: Optional[str] = None
