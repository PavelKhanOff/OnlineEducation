from app.database import async_session
from .category_dal import CategoryDAL


async def get_category_dal():
    async with async_session() as session:
        async with session.begin():
            yield CategoryDAL(session)
