from sqlalchemy.future import select
from app.database import async_session as session
from pydantic import UUID4
from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy.sql.expression import exists
from app.homework.models import Homework
from app.file.models import File
from app.file.schemas import FileToHomework as FileSchema
from app.users.models import User
from app.lessons.models import Lesson
from sqlalchemy import update, delete
from app.courses.models import Course


class HomeWorkDAL:
    def __init__(self, db_session: session):
        self.db_session = db_session

    async def get_hw(self, homework_id: int):
        q = await self.db_session.execute(select(Homework).filter_by(id=homework_id))
        return q.scalars().first()

    async def get_hw_with_files(self, homework_id: int):
        q = await self.db_session.execute(
            select(Homework)
            .options(selectinload(Homework.files))
            .filter_by(id=homework_id)
        )
        return q.scalars().first()

    async def create_hw(self, request: Homework):
        new_homework = Homework(
            title=request.title,
            description=request.description,
            lesson_id=request.lesson_id,
        )
        self.db_session.add(new_homework)
        await self.db_session.flush()
        return new_homework

    async def update_hw(self, homework_id: int, updated_values):
        q = update(Homework).where(Homework.id == homework_id)
        q = q.values(updated_values)
        q.execution_options(synchronize_session="fetch")
        await self.db_session.execute(q)

    async def delete_hw(self, homework_id: int):
        q = delete(Homework).where(Homework.id == homework_id)
        await self.db_session.execute(q)

    async def get_lesson(self, lesson_id: int):
        q = select(Lesson.course_id).where(Lesson.id == lesson_id)
        q = await self.db_session.execute(q)
        return q.scalars().first()

    async def check_hw(self, homework_id: int):
        q = await self.db_session.execute(
            exists(select(Homework.id).filter_by(id=homework_id)).select()
        )
        return q.scalar()

    async def check_course_exists(self, user_id, course_id: int):
        q = await self.db_session.execute(
            exists(select(Course.id).filter_by(user_id=user_id, id=course_id)).select()
        )
        return q.scalar()

    async def get_file(self, url: str):
        q = await self.db_session.execute(select(File).filter_by(url=url))
        return q.scalars().first()

    async def create_file(self, request: FileSchema):
        new_file = File(
            title=request.title,
            description=request.description,
            url=request.url,
            duration=request.duration,
            homework_id=request.homework_id,
            type=request.type,
        )
        self.db_session.add(new_file)
        await self.db_session.flush()
        return new_file

    # User route
    async def get_users_with_courses(self, user_id: UUID4):
        q = await self.db_session.execute(
            select(User).options(selectinload(User.courses)).filter_by(id=user_id)
        )
        return q.scalars().first()
