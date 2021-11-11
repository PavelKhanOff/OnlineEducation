from typing import List, Optional
import uuid
from sqlalchemy import update, desc, delete, func
from sqlalchemy.future import select
from .models import User
from sqlalchemy.orm import selectinload
from app.database import get_db, async_session as session
from app.courses.models import Course
from fastapi_users.password import get_password_hash
from .enums import Gender
from sqlalchemy.sql.expression import exists


class UserDAL:
    def __init__(self, db_session: session):
        self.db_session = db_session

    async def check_username(self, username):
        q = await self.db_session.execute(
            exists(select(User.id).filter_by(username=username)).select()
        )
        return q.scalar()

    async def get_user(self, user_id):
        user = await self.db_session.execute(
            select(User)
            .options(selectinload(User.achievements))
            .filter(User.id == user_id)
        )
        return user.scalars().first()

    async def get_user_followers(self, user_id):
        user = await self.db_session.execute(
            select(User)
            .options(selectinload(User.followers))
            .filter(User.id == user_id)
        )
        return user.scalars().first()

    async def get_user_following(self, user_id):
        user = await self.db_session.execute(
            select(User)
            .options(selectinload(User.following))
            .filter(User.id == user_id)
        )
        return user.scalars().first()

    async def get_user_courses(self, user_id):
        user = await self.db_session.execute(
            select(User).options(selectinload(User.courses)).filter(User.id == user_id)
        )
        return user.scalars().first()

    async def get_user_by_username(self, username):
        user = await self.db_session.execute(
            select(User).filter(User.username == username)
        )
        return user.scalars().first()

    async def get_users(self, username):
        users = await self.db_session.execute(select(User))
        users.unique()
        if username:
            users = await self.db_session.execute(
                select(User).filter(User.username.like(f'{username}%'))
            )
            users.unique()
        return users.scalars().all()

    async def get_popular_authors(self):
        users = await self.db_session.execute(
            select(User)
            .filter(User.is_author == True)
            .order_by(desc(User.sold_courses))
        )
        users.unique()
        return users.scalars().all()

    async def update_user(
        self,
        user_id,
        username: Optional[str] is None,
        first_name: Optional[str] is None,
        last_name: Optional[str] is None,
        email: Optional[str] is None,
        description: Optional[str] is None,
        website: Optional[str] is None,
        phone: Optional[str] is None,
        gender: Optional[Gender] is None,
        birth_date: Optional[str] is None,
    ):
        q = update(User).filter(User.id == user_id)
        if username:
            q = q.values(username=username)
        if first_name:
            q = q.values(first_name=first_name)
        if last_name:
            q = q.values(last_name=last_name)
        if email:
            q = q.values(email=email)
        if description:
            q = q.values(description=description)
        if website:
            q = q.values(website=website)
        if phone:
            q = q.values(phone=phone)
        if gender:
            q = q.values(gender=gender)
        if birth_date:
            q = q.values(birth_date=birth_date)
        q.execution_options(synchronize_session="fetch")
        await self.db_session.execute(q)
        user = await self.get_user(user_id)
        return user

    async def delete_user(self, user_id):
        stmt = delete(User).where(User.id == user_id)
        await self.db_session.execute(stmt)

    async def get_courses(self, user_id):
        stmt = (
            select(Course)
            .options(selectinload(Course.user))
            .where(Course.user_id == user_id)
            .where(Course.is_deleted == False)
        )
        return stmt

    async def get_user_with_sub_course(self, user_id):
        stmt = await self.db_session.execute(
            select(User)
            .options(selectinload(User.subscribed_courses))
            .where(User.id == user_id)
        )
        return stmt.scalars().first()

    async def get_deleted_courses(self, user_id):
        stmt = (
            select(Course)
            .options(selectinload(Course.user))
            .where(Course.user_id == user_id)
            .where(Course.is_deleted == True)
        )
        return stmt

    async def author(self, user_id, is_author: bool):
        q = update(User).where(User.id == user_id)
        q = q.values(is_author=is_author)
        q.execution_options(synchronize_session="fetch")
        await self.db_session.execute(q)

    async def create_superuser(self):
        new_user = User(
            id=uuid.uuid4(),
            username="superuser_root",
            hashed_password=get_password_hash("dy876tv2748h6emw"),
            first_name='DASTAN',
            last_name='AKHMET',
            email="DASTAN@DASTAN.DASTAN",
            is_superuser=True,
        )
        self.db_session.add(new_user)
        return new_user
