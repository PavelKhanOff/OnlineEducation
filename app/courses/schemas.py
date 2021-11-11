import datetime
from typing import Optional, Dict, Any, List
from app.lessons.schemas import LessonOut
from app.file.schemas import AvatarOut
from app.users.schemas import UserOut
from pydantic import BaseModel, EmailStr, root_validator, UUID4


class Course(BaseModel):
    title: str
    description: str
    start_date: Optional[datetime.datetime]
    end_date: Optional[datetime.datetime]
    price: int

    class Config:
        orm_mode = True
        validate_assignment = True

    @root_validator
    def calculate_start_date(cls, values):
        if values.get('start_date') is not None:
            values["start_date"] = values["start_date"].strftime("%Y-%m-%dT%H:%M:%SZ")
            values['start_date'] = datetime.datetime.strptime(
                values["start_date"], "%Y-%m-%dT%H:%M:%SZ"
            )
        return values

    @root_validator
    def calculate_end_date(cls, values):
        if values.get('end_date') is not None:
            values["end_date"] = values["end_date"].strftime("%Y-%m-%dT%H:%M:%SZ")
            values['end_date'] = datetime.datetime.strptime(
                values["end_date"], "%Y-%m-%dT%H:%M:%SZ"
            )
        return values


class CourseOut(Course):
    id: int
    created_at: datetime.datetime
    user: Optional[UserOut] = None
    lessons: List[LessonOut]
    cover: Optional[AvatarOut] = None

    class Config:
        orm_mode = True
        validate_assignment = True

    @root_validator
    def calculate_created_at(cls, values):
        if values.get('created_at') is not None:
            values["created_at"] = values["created_at"].strftime("%Y-%m-%dT%H:%M:%SZ")
            values["created_at"] = datetime.datetime.strptime(
                values["created_at"], "%Y-%m-%dT%H:%M:%SZ"
            )
        return values


class MyCourseOut(Course):
    id: int
    created_at: datetime.datetime
    user: Optional[UserOut] = None
    cover: Optional[AvatarOut] = None

    class Config:
        orm_mode = True
        validate_assignment = True

    @root_validator
    def calculate_created_at(cls, values):
        if values.get('created_at') is not None:
            values["created_at"] = values["created_at"].strftime("%Y-%m-%dT%H:%M:%SZ")
            values["created_at"] = datetime.datetime.strptime(
                values["created_at"], "%Y-%m-%dT%H:%M:%SZ"
            )
        return values


class UpdateCourse(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    start_date: Optional[datetime.datetime]
    end_date: Optional[datetime.datetime]
    price: Optional[int] = None

    class Config:
        orm_mode = True
        validate_assignment = True

    @root_validator
    def calculate_start_date(cls, values):
        if values.get('start_date') is not None:
            values["start_date"] = values["start_date"].strftime("%Y-%m-%dT%H:%M:%SZ")
            values['start_date'] = datetime.datetime.strptime(
                values["start_date"], "%Y-%m-%dT%H:%M:%SZ"
            )
        if values.get('end_date') is not None:
            values["end_date"] = values["end_date"].strftime("%Y-%m-%dT%H:%M:%SZ")
            values['end_date'] = datetime.datetime.strptime(
                values["end_date"], "%Y-%m-%dT%H:%M:%SZ"
            )
        return values


class CourseEmail(BaseModel):
    email: EmailStr


class AddCategory(BaseModel):
    category_id: int
    course_id: int


class AddGraduated(BaseModel):
    user_id: UUID4
    course_id: int
