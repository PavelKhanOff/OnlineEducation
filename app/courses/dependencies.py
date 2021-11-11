from app.database import async_session
from app.courses.course_dal import CourseDAL


async def get_course_dal():
    async with async_session() as session:
        async with session.begin():
            yield CourseDAL(session)
