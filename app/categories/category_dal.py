from typing import Optional

from sqlalchemy import update, delete, desc
from sqlalchemy.future import select
from sqlalchemy.sql.expression import exists, func
from sqlalchemy.orm import selectinload

from app.database import async_session as session
from app.courses.models import Course
from app.categories.models import Category


class CategoryDAL:
    def __init__(self, db_session: session):
        self.db_session = db_session

    async def create_category(self, image, title, description):
        new_category = Category(image=image, title=title, description=description)
        self.db_session.add(new_category)
        return new_category

    async def get_all_categories(self, title: [Optional] = None):
        q = select(Category).order_by(Category.id)
        if title:
            q = select(Category).filter(Category.title.like(f'{title}%'))
        return q

    async def get_category(self, category_id):
        q = await self.db_session.execute(
            select(Category).filter(Category.id == category_id)
        )
        try:
            return q.scalars().first()
        except:
            return None

    async def get_category_courses(self, category_id):
        q = await self.db_session.execute(
            select(Category)
            .options(selectinload(Category.courses))
            .filter(Category.id == category_id)
        )
        try:
            return q.scalars().first()
        except:
            return None

    async def check_category_exists_by_title(self, category_title: str):
        q = await self.db_session.execute(
            exists(select(Category.id).filter_by(title=category_title)).select()
        )
        return q.scalar()

    async def check_category_exists_by_id(self, category_id: int):
        q = await self.db_session.execute(
            exists(select(Category.id).filter_by(id=category_id)).select()
        )
        return q.scalar()

    async def get_popular_categories(self):
        q = (
            select(Category)
            .outerjoin(Category.courses)
            .group_by(Category)
            .order_by(desc(func.count(Course.id)))
        )
        return q

    async def update_category(
        self,
        category_id,
        image: Optional[str] is None,
        title: Optional[str] is None,
        description: Optional[str] is None,
    ):
        q = update(Category).filter(Category.id == category_id)
        if image:
            q = q.values(image=image)
        if title:
            q = q.values(title=title)
        if description:
            q = q.values(description=description)
        q.execution_options(synchronize_session="fetch")
        await self.db_session.execute(q)
        category = await self.get_category(category_id)
        return category

    async def delete_category(self, category_id):
        stmt = delete(Category).where(Category.id == category_id)
        await self.db_session.execute(stmt)
        return "удалено"
