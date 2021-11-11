from pydantic import BaseModel, EmailStr


class PreRegisterSchema(BaseModel):
    email: EmailStr

    class Config:
        orm_mode = True
