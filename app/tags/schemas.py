import datetime
from typing import Any, List, Optional, Union

from fastapi_users import FastAPIUsers, models
from pydantic import (UUID4, AnyUrl, BaseModel, EmailStr, Field,
                      root_validator, validator)


class TagOut(BaseModel):
    title: str

    class Config:
        orm_mode = True
