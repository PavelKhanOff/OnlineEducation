from pydantic import UUID4, BaseModel


class Follow(BaseModel):
    author_id: UUID4
