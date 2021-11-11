from typing import Optional
from pydantic import BaseModel


class Category(BaseModel):
    image: str
    title: str
    description: str


class UpdateCategory(BaseModel):
    image: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None


class CategoryOut(Category):
    id: int

    class Config:
        orm_mode = True

