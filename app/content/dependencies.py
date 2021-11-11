from app.database import async_session
from app.content.content_dal import ContentDAL


async def get_content_dal():
    async with async_session() as session:
        async with session.begin():
            yield ContentDAL(session)
