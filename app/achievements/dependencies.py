from app.database import async_session
from app.achievements.achievement_dal import AchievementDAL


async def get_achievement_dal():
    async with async_session() as session:
        async with session.begin():
            yield AchievementDAL(session)
