from app.database import async_session
from .lesson_dal import LessonDAL


async def get_lesson_dal():
    async with async_session() as session:
        async with session.begin():
            yield LessonDAL(session)
