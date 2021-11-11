from typing import Optional

from pydantic import BaseModel


class Content(BaseModel):
    text: str
    lesson_id: int
