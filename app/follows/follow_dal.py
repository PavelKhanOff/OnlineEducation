from sqlalchemy.future import select
from app.database import async_session as session
from app.users.models import User, user_following
from app.achievements.models import Achievement
from pydantic import UUID4
from sqlalchemy.orm import selectinload
from sqlalchemy.sql import func
from sqlalchemy.sql.expression import exists
from sqlalchemy import insert, delete


class FollowDAL:
    def __init__(self, db_session: session):
        self.db_session = db_session

    async def user_following_count(self, user_id):
        q = await self.db_session.execute(
            select(func.count(user_following.c.user_id)).filter_by(user_id=user_id)
        )
        return q.scalars().first()

    async def user_followers_count(self, user_id):
        q = await self.db_session.execute(
            select(func.count(user_following.c.following_id)).filter_by(
                following_id=user_id
            )
        )
        return q.scalars().first()

    async def follow_exists(self, user_id, second_user_id):
        q = await self.db_session.execute(
            exists(
                select(user_following.c.following_id).filter_by(
                    following_id=second_user_id, user_id=user_id
                )
            ).select()
        )
        return q.scalar()

    async def follow(self, user_id, second_user_id):
        checker = await self.follow_exists(user_id, second_user_id)
        if not checker:
            await self.db_session.execute(
                insert(user_following).values(
                    user_id=user_id, following_id=second_user_id
                )
            )
            return True
        else:
            await self.db_session.execute(
                delete(user_following).where(
                    user_following.c.user_id == user_id,
                    user_following.c.following_id == second_user_id,
                )
            )
            return False

    async def get_username(self, user_id):
        q = await self.db_session.execute(select(User.username).filter_by(id=user_id))
        return q.scalars().first()

    # Achievement Route

    async def get_achievement(self, title: str):
        q = await self.db_session.execute(select(Achievement).filter_by(title=title))
        return q.scalars().first()

    # User Route
    async def get_user(self, user_id: UUID4):
        q = await self.db_session.execute(select(User).filter_by(id=user_id))
        return q.scalars().first()

    async def get_user_with_following(self, user_id: UUID4):
        q = await self.db_session.execute(
            select(User)
            .options(selectinload(User.following))
            .filter(User.id == user_id)
        )
        return q.scalars().first()

    async def get_user_with_followers(self, user_id: UUID4):
        q = await self.db_session.execute(
            select(User)
            .options(selectinload(User.followers))
            .filter(User.id == user_id)
        )
        return q.scalars().first()
