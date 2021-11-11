from app.database import async_session
from app.homework.dal import HomeWorkDAL


async def get_homework_dal():
    async with async_session() as session:
        async with session.begin():
            yield HomeWorkDAL(session)
