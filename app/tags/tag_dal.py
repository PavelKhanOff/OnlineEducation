from sqlalchemy import update, delete
from sqlalchemy.future import select
from app.tags.models import Tag
from app.users.models import User
from app.database import async_session as session


class TagDAL:
    def __init__(self, db_session: session):
        self.db_session = db_session

    async def get_all_query(self):
        q = select(Tag)
        return q

    async def get_by_title_query(self, title: str):
        q = select(Tag).filter(Tag.title.like(f'{title}%'))
        return q

    async def get_by_id(self, tag_id: int):
        q = await self.db_session.execute(select(Tag).filter_by(id=tag_id))
        return q.scalars().first()

    async def get_by_title(self, title: str):
        q = await self.db_session.execute(select(Tag).filter_by(title=title))
        return q.scalars().first()

    async def create_tag(self, title: str):
        new_tag = Tag(title=title)
        self.db_session.add(new_tag)
        await self.db_session.flush()
        return new_tag

    async def get_user(self, user_id: str):
        q = await self.db_session.execute(select(User).filter_by(id=user_id))
        return q.scalars().first()

    async def update_tag(self, tag_id: int, updated_values):
        q = update(Tag).where(Tag.id == tag_id)
        q = q.values(updated_values)
        q.execution_options(synchronize_session="fetch")
        await self.db_session.execute(q)

    async def delete_tag(self, tag_id: int):
        q = delete(Tag).where(Tag.id == tag_id)
        await self.db_session.execute(q)
