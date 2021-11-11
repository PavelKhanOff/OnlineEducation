from sqlalchemy.sql.expression import exists
from sqlalchemy import update, delete
from sqlalchemy.future import select
from pydantic import UUID4
from .models import Lesson
from sqlalchemy.orm import selectinload
from app.database import async_session as session
from app.courses.models import Course
from app.users.models import User
from app.file.models import File
from app.lessons.schemas import FileToLesson
from app.tags.models import Tag


class LessonDAL:
    def __init__(self, db_session: session):
        self.db_session = db_session

    async def get_lesson(self, lesson_id):
        lesson = await self.db_session.execute(
            select(Lesson)
            .options(selectinload(Lesson.contents))
            .filter(Lesson.id == lesson_id)
        )
        return lesson.scalars().first()

    async def get_lesson_with_course_id(self, lesson_id):
        user = await self.db_session.execute(
            select(Lesson)
            .options(selectinload(Lesson.contents))
            .filter(Lesson.id == lesson_id)
        )
        return user.scalars().first()

    async def get_course(self, course_id):
        user = await self.db_session.execute(
            select(Course)
            .options(selectinload(Course.user))
            .filter(Course.id == course_id)
        )
        return user.scalars().first()

    async def check_course_exists(self, user_id, course_id: int):
        q = await self.db_session.execute(
            exists(select(Course.id).filter_by(user_id=user_id, id=course_id)).select()
        )
        return q.scalar()

    async def check_lesson_exists(self, lesson_id: int):
        q = await self.db_session.execute(
            exists(select(Lesson.id).filter_by(id=lesson_id))
        ).select()
        return q.scalar()

    async def get_lesson_with_homework(self, lesson_id):
        user = await self.db_session.execute(
            select(Lesson)
            .options(selectinload(Lesson.homework), selectinload(Lesson.contents))
            .filter(Lesson.id == lesson_id)
        )
        return user.scalars().first()

    async def get_lesson_with_tags(self, lesson_id):
        user = await self.db_session.execute(
            select(Lesson)
            .options(selectinload(Lesson.tags), selectinload(Lesson.contents))
            .filter(Lesson.id == lesson_id)
        )
        return user.scalars().first()

    async def get_tag(self, tag_id):
        user = await self.db_session.execute(select(Tag).filter(Tag.id == tag_id))
        return user.scalars().first()

    async def create_lesson(self, title, description, estimated_time, course_id):
        new_lesson = Lesson(
            title=title,
            description=description,
            estimated_time=estimated_time,
            course_id=course_id,
        )
        self.db_session.add(new_lesson)
        return new_lesson

    async def update_lesson(self, lesson_id, title, description, estimated_time):
        q = update(Lesson).filter(Lesson.id == lesson_id)
        if title:
            q = q.values(title=title)
        if description:
            q = q.values(description=description)
        if estimated_time:
            q = q.values(estimated_time=estimated_time)
        q.execution_options(synchronize_session="fetch")
        await self.db_session.execute(q)
        lesson = await self.get_lesson(lesson_id)
        return lesson

    async def delete_lesson(self, lesson_id):
        stmt = delete(Lesson).where(Lesson.id == lesson_id)
        await self.db_session.execute(stmt)

    async def get_user_courses(self, user_id):
        user = await self.db_session.execute(
            select(User).options(selectinload(User.courses)).where(User.id == user_id)
        )
        return user.scalars().first()

    async def get_course(self, course_id):
        course = await self.db_session.execute(
            select(Course).where(Course.id == course_id)
        )
        return course.scalars().first()

    async def get_file(self, file_url):
        file = await self.db_session.execute(select(File).where(File.url == file_url))
        return file.scalars().first()

    async def create_file(self, request: FileToLesson, lesson_id: int, user_id: UUID4):
        new_file = File(
            title=request.title,
            description=request.description,
            url=request.url,
            type=request.type,
            duration=request.duration,
            lesson_id=lesson_id,
            user=user_id,
        )
        self.db_session.add(new_file)
        await self.db_session.flush()
        return new_file
