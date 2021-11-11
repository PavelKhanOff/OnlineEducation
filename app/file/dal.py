from sqlalchemy.future import select
from app.file.models import File, Avatar
from app.database import async_session as session
import app.file.schemas as schemas
from pydantic import UUID4
from app.courses.models import Course
from app.homework.models import Homework
from app.lessons.models import Lesson
from app.achievements.models import Achievement
from app.users.models import User
from sqlalchemy.orm import selectinload
from sqlalchemy.sql.expression import exists


class FileDAL:
    def __init__(self, db_session: session):
        self.db_session = db_session

    async def create_file(self, request: schemas.File, user_id: UUID4):
        new_file = File(
            title=request.title,
            description=request.description,
            url=request.url,
            type=request.type,
            duration=request.duration,
            course_id=request.course_id,
            content_id=request.content_id,
            homework_id=request.homework_id,
            user=user_id,
        )
        self.db_session.add(new_file)
        await self.db_session.flush()

    async def upload_content_file(self, request: schemas.Content):
        new_file = File(
            title=request.title,
            description=request.description,
            url=request.url,
            key=request.key,
            type=request.type,
            duration=request.duration,
            content_id=request.content_id,
            user=request.user_id,
        )
        self.db_session.add(new_file)
        await self.db_session.flush()

    async def upload_avatar(self, request):
        user = await self.db_session.execute(select(User).filter_by(id=request.user_id))
        user = user.scalars().first()
        new_file = Avatar(
            key=request.key,
            url=request.url,
            title=request.title,
            user_avatar=user,
        )
        self.db_session.add(new_file)
        await self.db_session.flush()

    async def upload_course_cover(self, request):
        course = await self.db_session.execute(
            select(Course).filter_by(id=request.course_id)
        )
        course = course.scalars().first()
        new_file = Avatar(
            key=request.key,
            url=request.url,
            title=request.title,
            cover_course=course,
        )
        self.db_session.add(new_file)
        await self.db_session.flush()

    async def upload_achievement_avatar(self, request):
        achievement = await self.db_session.execute(
            select(Achievement).filter_by(id=request.achievement_id)
        )
        achievement = achievement.scalars().first()
        new_file = Avatar(
            key=request.key,
            url=request.url,
            title=request.title,
            cover_achievement=achievement,
        )
        self.db_session.add(new_file)
        await self.db_session.flush()

    async def get_user_files(self, user_id: UUID4, file_type: str):
        q = await self.db_session.execute(
            select(File).filter_by(type=file_type, user=user_id)
        )
        return q.scalars().all()

    # Course Route
    async def check_course(self, course_id: int):
        q = await self.db_session.execute(
            exists(select(Course.id).filter_by(id=course_id)).select()
        )
        return q.scalar()

    # Lesson Route
    async def check_lesson(self, lesson_id):
        q = await self.db_session.execute(
            exists(select(Lesson.id).filter_by(id=lesson_id)).select()
        )
        return q.scalar()

    # HW route
    async def check_hw(self, homework_id: int):
        q = await self.db_session.execute(
            exists(select(Homework.id).filter_by(id=homework_id)).select()
        )
        return q.scalar()

    # Achievement route
    async def get_achievement(self, title: str):
        q = await self.db_session.execute(select(Achievement).filter_by(title=title))
        return q.scalars().first()

    # User route
    async def get_user_with_achievements(self, user_id):
        user = await self.db_session.execute(
            select(User)
            .options(selectinload(User.achievements))
            .filter(User.id == user_id)
        )
        return user.scalars().first()
