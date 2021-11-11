from pydantic import UUID4, BaseModel, EmailStr


class Subscription(BaseModel):
    course_id: int
    user_id: UUID4


class EmailSubscription(BaseModel):
    course_id: int
    email: EmailStr
    user_id: str
