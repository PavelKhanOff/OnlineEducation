from app.database import async_session
from app.email.em_dal import EmailDAL


async def get_email_dal():
    async with async_session() as session:
        async with session.begin():
            yield EmailDAL(session)
