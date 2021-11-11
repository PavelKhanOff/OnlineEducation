from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.database import async_session as session
from app.courses.models import Course
from app.lessons.models import Lesson
from app.users.models import User, user_following
from app.homework.models import Homework
from app.achievements.models import Achievement
from sqlalchemy.sql.expression import exists
from app.config import SECRET
from fastapi_users.utils import JWT_ALGORITHM, generate_jwt


class MiddlewareDAL:
    def __init__(self, db_session: session):
        self.db_session = db_session

    async def check_user(self, user_id):
        q = await self.db_session.execute(
            exists(select(User.id).filter_by(id=user_id)).select()
        )
        return q.scalar()

    async def get_user(self, user_id):
        user = await self.db_session.execute(select(User).filter(User.id == user_id))
        return user.scalars().first()

    async def get_user_username(self, user_id):
        user = await self.db_session.execute(select(User).filter(User.id == user_id))
        return user.scalars().first().username

    async def check_achievement(self, achievement_id: int):
        q = await self.db_session.execute(
            exists(select(Achievement.id).filter_by(id=achievement_id)).select()
        )
        return q.scalar()

    async def check_course(self, course_id):
        q = await self.db_session.execute(
            exists(select(Course.id).filter_by(id=course_id)).select()
        )
        return q.scalar()

    async def check_course_with_user(self, course_id, user_id):
        q = await self.db_session.execute(
            exists(select(Course.id).filter_by(id=course_id, user_id=user_id)).select()
        )
        return q.scalar()

    async def get_course(self, course_id):
        user = await self.db_session.execute(
            select(Course)
            .options(selectinload(Course.user))
            .filter(Course.id == course_id)
        )
        return user.scalars().first()

    async def get_lesson_with_course(self, lesson_id):
        user = await self.db_session.execute(
            select(Lesson).filter(Lesson.id == lesson_id)
        )
        return user.scalars().first()

    async def get_user_by_course(self, user_id):
        user = await self.db_session.execute(select(User).filter(User.id == user_id))
        return user.scalars().first()

    async def check_lesson(self, lesson_id):
        q = await self.db_session.execute(
            exists(select(Lesson.id).filter_by(id=lesson_id)).select()
        )
        return q.scalar()

    async def get_lesson(self, lesson_id):
        user = await self.db_session.execute(
            select(Lesson).filter(Lesson.id == lesson_id)
        )
        return user.scalars().first()

    async def get_lesson_course(self, lesson_id, user_id):
        lesson_course_id = await self.db_session.execute(
            select(Lesson.course_id).filter(Lesson.id == lesson_id)
        )
        lesson_course_id = lesson_course_id.scalars().first()
        if lesson_course_id:
            checker = await self.check_course(lesson_course_id, user_id=user_id)
            if checker:
                return lesson_course_id
        return None

    async def check_homework(self, homework_id):
        q = await self.db_session.execute(
            exists(select(Homework.id).filter_by(id=homework_id)).select()
        )
        return q.scalar()

    async def get_homework(self, homework_id):
        user = await self.db_session.execute(
            select(Homework).filter(Homework.id == homework_id)
        )
        return user.scalars().first()

    async def get_user_with_following(self, user_id):
        users = await self.db_session.execute(
            select(user_following.c.following_id).filter_by(user_id=user_id)
        )
        return users.scalars().all()

    async def get_user_with_followers(self, user_id):
        users = await self.db_session.execute(
            select(user_following.c.user_id).filter_by(following_id=user_id)
        )
        return users.scalars().all()

    async def get_user_with_sub_course(self, user_id):
        user = await self.db_session.execute(
            select(User)
            .options(selectinload(User.subscribed_courses))
            .filter(User.id == user_id)
        )
        return user.scalars().first()

    async def get_user_with_sub_cours_by_email(self, email):
        user = await self.db_session.execute(
            select(User)
            .options(selectinload(User.subscribed_courses))
            .filter(User.email == email)
        )
        return user.scalars().first()

    async def get_by_title(self, title):
        q = await self.db_session.execute(select(Achievement).filter_by(title=title))
        return q.scalars().first()

    async def get_user_with_achievements(self, user_id):
        user = await self.db_session.execute(
            select(User)
            .options(selectinload(User.achievements))
            .filter(User.id == user_id)
        )
        return user.scalars().first()

    async def get_user_with_courses(self, user_id):
        user = await self.db_session.execute(
            select(User).options(selectinload(User.courses)).filter(User.id == user_id)
        )
        return user.scalars().first()

    async def get_course_with_subs(self, user_id):
        course = await self.db_session.execute(
            select(Course)
            .options(selectinload(Course.subscribers), selectinload(Course.user))
            .filter(User.id == user_id)
        )
        return course.scalars().all()

    async def get_achievements_by_title(self, title):
        user = await self.db_session.execute(
            select(Achievement).filter(Achievement.title == title)
        )
        return user.scalars().first()

    async def get_user_by_username(self):
        user = await self.db_session.execute(
            select(User).filter(User.is_superuser == True)
        )
        return user.scalars().first()

    async def get_superuser_token(self):
        user = await self.get_user_by_username()
        data = {"user_id": str(user.id), "aud": ["fastapi-users:auth"]}
        token = generate_jwt(data, SECRET, 60, JWT_ALGORITHM)
        return token
