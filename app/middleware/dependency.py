from app.database import async_session
from .middleware_dal import MiddlewareDAL


async def get_middleware_dal():
    async with async_session() as session:
        async with session.begin():
            yield MiddlewareDAL(session)
