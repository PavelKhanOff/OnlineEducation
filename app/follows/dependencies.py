from app.database import async_session
from app.follows.follow_dal import FollowDAL


async def get_follow_dal():
    async with async_session() as session:
        async with session.begin():
            yield FollowDAL(session)
