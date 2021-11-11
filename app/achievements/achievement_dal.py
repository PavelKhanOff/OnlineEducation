from sqlalchemy import update, desc, delete, insert
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.achievements.models import Achievement
from app.users.models import User, user_achievements_association
from app.database import async_session as session
import app.achievements.schemas as schemas
from sqlalchemy.sql.expression import exists


class AchievementDAL:
    def __init__(self, db_session: session):
        self.db_session = db_session

    async def get_all_query(self):
        q = select(Achievement)
        return q

    async def get_by_title_query(self, title: str):
        q = select(Achievement).filter(Achievement.title.like(f'{title}%'))
        return q

    async def get_by_title(self, title):
        q = await self.db_session.execute(select(Achievement).filter_by(title=title))
        return q.scalars().first()

    async def get_by_id(self, achievement_id: int):
        q = await self.db_session.execute(
            select(Achievement).filter_by(id=achievement_id)
        )
        return q.scalars().first()

    async def check_by_id(self, achievement_id: int):
        q = await self.db_session.execute(
            exists(select(Achievement.id).filter_by(id=achievement_id)).select()
        )
        return q.scalar()

    async def get_by_id_with_users(self, achievement_id: int):
        q = await self.db_session.execute(
            select(Achievement)
            .options(selectinload(Achievement.users))
            .filter(Achievement.id == achievement_id)
        )
        return q.scalars().first()

    async def get_user(self, user_id: str):
        q = await self.db_session.execute(select(User).filter_by(id=user_id))
        return q.scalars().first()

    async def create_achievement(self, request: schemas.Achievement):
        achievement = await self.get_by_title(request.title)
        if achievement:
            return False

        new_achievement = Achievement(
            title=request.title, description=request.description
        )
        self.db_session.add(new_achievement)
        await self.db_session.flush()
        return new_achievement

    async def update_achievement(self, achievement_id: int, updated_values):
        q = update(Achievement).where(Achievement.id == achievement_id)
        q = q.values(updated_values)
        q.execution_options(synchronize_session="fetch")
        await self.db_session.execute(q)

    async def delete_achievement(self, achievement_id: int):
        q = delete(Achievement).where(Achievement.id == achievement_id)
        await self.db_session.execute(q)

    async def achievement_exists(self, user_id, achievement_id: int):
        q = await self.db_session.execute(
            exists(
                select(user_achievements_association.c.User_id).filter_by(
                    Achievement_id=achievement_id, User_id=user_id
                )
            ).select()
        )
        return q.scalar()

    async def achievement(self, user_id, achievement_id: int):
        checker = await self.achievement_exists(user_id, achievement_id)
        if not checker:
            await self.db_session.execute(
                insert(user_achievements_association).values(
                    User_id=user_id, Achievement_id=achievement_id
                )
            )
            return True
        else:
            await self.db_session.execute(
                delete(user_achievements_association).where(
                    user_achievements_association.c.User_id == user_id,
                    user_achievements_association.c.Achievement_id == achievement_id,
                )
            )
            return False
