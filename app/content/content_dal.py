from sqlalchemy import update, desc, delete
from sqlalchemy.future import select
from app.courses.models import Course
from app.database import async_session as session
from app.content.models import Content
import app.content.schemas as schemas
from sqlalchemy.sql.expression import exists
from app.lessons.models import Lesson


class ContentDAL:
    def __init__(self, db_session: session):
        self.db_session = db_session

    async def create_content(self, request: schemas.Content):
        new_content = Content(text=request.text, lesson_id=request.lesson_id)
        self.db_session.add(new_content)
        await self.db_session.flush()
        await self.db_session.refresh(new_content)
        return new_content

    async def get_content(self, content_id: int):
        content = await self.db_session.execute(
            select(Content).filter_by(id=content_id)
        )
        return content.scalars().first()

    async def get_lesson_contents(self, lesson_id: int):
        contents = await self.db_session.execute(
            select(Content).filter_by(lesson_id=lesson_id)
        )
        return contents.unique().scalars().all()

    async def delete_content(self, content_id: int):
        stmt = delete(Content).where(Content.id == content_id)
        await self.db_session.execute(stmt)

    async def check_content_user(self, content_id: int, user_id: str):
        lesson = await self.db_session.execute(
            select(Content.lesson_id).filter_by(id=content_id)
        )
        lesson_id = lesson.scalars().first()
        if lesson_id:
            course = await self.db_session.execute(
                select(Lesson.course_id).filter_by(id=lesson_id)
            )
            course_id = course.scalars().first()
            if course_id:
                checker = await self.db_session.execute(
                    exists(
                        select(Course.id).filter_by(id=course_id, user_id=user_id)
                    ).select()
                )
                return checker
        return False

    async def get_content_information(self, content_id: int, user_id: str):
        lesson = await self.db_session.execute(
            select(Content.lesson_id).filter_by(id=content_id)
        )
        lesson_id = lesson.scalars().first()
        if lesson_id:
            course = await self.db_session.execute(
                select(Lesson.course_id).filter_by(id=lesson_id)
            )
            course_id = course.scalars().first()
            if course_id:
                checker = await self.db_session.execute(
                    exists(
                        select(Course.id).filter_by(id=course_id, user_id=user_id)
                    ).select()
                )
                return (user_id, course_id, lesson_id, content_id)
        return None

    async def check_lesson_user(self, lesson_id: int, user_id: str):
        if lesson_id:
            course = await self.db_session.execute(
                select(Lesson.course_id).filter_by(id=lesson_id)
            )
            course_id = course.scalars().first()
            if course_id:
                checker = await self.db_session.execute(
                    exists(
                        select(Course.id).filter_by(id=course_id, user_id=user_id)
                    ).select()
                )
                return checker
        return False
