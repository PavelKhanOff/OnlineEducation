from app.database import async_session
from .user_dal import UserDAL


async def get_user_dal():
    async with async_session() as session:
        async with session.begin():
            yield UserDAL(session)
