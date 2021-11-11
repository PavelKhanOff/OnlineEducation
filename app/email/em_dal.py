from sqlalchemy.future import select
from app.email.models import PreRegister
from app.database import async_session as session
from app.email.schemas import PreRegisterSchema


class EmailDAL:
    def __init__(self, db_session: session):
        self.db_session = db_session

    async def create_pre_user(self, request: PreRegisterSchema):
        new_pre_user_email = PreRegister(email=request.email)
        self.db_session.add(new_pre_user_email)
        await self.db_session.flush()
        return new_pre_user_email

    async def get_pre_user_by_email(self, email: str):
        q = await self.db_session.execute(select(PreRegister).filter_by(email=email))
        return q.scalars().first()

    async def get_pre_users_query(self):
        q = select(PreRegister)
        return q
