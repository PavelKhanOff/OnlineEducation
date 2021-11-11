from app.database import async_session
from app.tags.tag_dal import TagDAL


async def get_tag_dal():
    async with async_session() as session:
        async with session.begin():
            yield TagDAL(session)
