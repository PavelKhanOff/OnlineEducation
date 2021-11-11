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
from .enums import Gender
from app.file.schemas import AvatarOut


class User(models.BaseUser):
    username: str
    first_name: str
    last_name: str
    email: EmailStr
    description: Optional[str] = None
    website: Optional[str] = None
    phone: str = None
    gender: Optional[Gender] = None
    birth_date: Optional[datetime.date] = None
    is_author: Optional[bool] = False


class UserCreate(models.BaseUserCreate):
    username: str
    first_name: str
    last_name: str
    email: EmailStr
    description: Optional[str] = None
    website: Optional[str] = None
    phone: str = None
    gender: Optional[Gender] = None
    birth_date: Optional[datetime.date] = None


# Properties to receive via API on update
class UserUpdate(models.CreateUpdateDictModel):
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    website: Optional[str] = None
    phone: Optional[str] = None
    gender: Optional[Gender] = None
    birth_date: Optional[datetime.date] = None
    email: Optional[EmailStr]


class UserDB(User, models.BaseUserDB):
    pass


class PropertyBaseModel(BaseModel):
    """
    Workaround for serializing properties with pydantic until
    https://github.com/samuelcolvin/pydantic/issues/935
    is solved
    """

    @classmethod
    def get_properties(cls):
        return [
            prop
            for prop in dir(cls)
            if isinstance(getattr(cls, prop), property)
            and prop not in ("__values__", "fields")
        ]

    def dict(
        self,
        *,
        include: Union['AbstractSetIntStr', 'MappingIntStrAny'] = None,
        exclude: Union['AbstractSetIntStr', 'MappingIntStrAny'] = None,
        by_alias: bool = False,
        skip_defaults: bool = None,
        exclude_unset: bool = False,
        exclude_defaults: bool = False,
        exclude_none: bool = False,
    ) -> 'DictStrAny':
        attribs = super().dict(
            include=include,
            exclude=exclude,
            by_alias=by_alias,
            skip_defaults=skip_defaults,
            exclude_unset=exclude_unset,
            exclude_defaults=exclude_defaults,
            exclude_none=exclude_none,
        )
        props = self.get_properties()
        # Include and exclude properties
        if include:
            props = [prop for prop in props if prop in include]
        if exclude:
            props = [prop for prop in props if prop not in exclude]

        # Update the attribute dict with the properties
        if props:
            attribs.update({prop: getattr(self, prop) for prop in props})

        return attribs


class UserOut(User, PropertyBaseModel):
    id: UUID4
    followers_count: Optional[int] = None
    following_count: Optional[int] = None
    posts_count: Optional[int] = None
    courses_count: Optional[int] = None
    is_followed: bool = False
    avatar: Optional[AvatarOut] = None

    class Config:
        orm_mode = True


class CourseUserOut(BaseModel):
    id: UUID4
    username: str
    first_name: str
    last_name: str


class UserUpdateSecond(BaseModel):
    username: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    email: Optional[EmailStr]
    description: Optional[str]
    website: Optional[str]
    phone: Optional[str]
    gender: Optional[Gender] = None
    birth_date: Optional[datetime.date] = None
