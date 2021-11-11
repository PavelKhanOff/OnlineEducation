from sqlalchemy import update, desc, delete
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.database import async_session as session
from pydantic import UUID4
from app.courses.models import Course
from app.categories.models import Category
from app.file.models import File
import app.courses.schemas as schemas
from app.file.schemas import FileToCourse as FileSchema
from app.users.models import User


class CourseDAL:
    def __init__(self, db_session: session):
        self.db_session = db_session

    async def show_all_courses(self, title: str):
        courses = (
            select(Course)
            .options(selectinload(Course.lessons), selectinload(Course.user))
            .filter_by(is_deleted=False, is_visible=True)
        )
        if title:
            courses = courses.filter(Course.title.like(f'{title}%'))
        courses = await self.db_session.execute(courses)
        return courses.unique().scalars().all()

    async def show_course(self, course_id: int):
        q = await self.db_session.execute(
            select(Course)
            .options(selectinload(Course.user))
            .filter_by(id=course_id, is_deleted=False, is_visible=True)
        )
        return q.scalars().first()

    async def get_course(self, course_id: int):
        q = await self.db_session.execute(
            select(Course).options(selectinload(Course.user)).filter_by(id=course_id)
        )
        return q.scalars().first()

    async def show_course_with_lessons(self, course_id: int):
        q = await self.db_session.execute(
            select(Course)
            .options(selectinload(Course.lessons), selectinload(Course.user))
            .filter_by(id=course_id, is_deleted=False, is_visible=True)
        )
        return q.scalars().first()

    async def show_category(self, category_id: int):
        q = await self.db_session.execute(select(Category).filter_by(id=category_id))
        return q.scalars().first()

    async def show_course_with_files(self, course_id: int):
        q = await self.db_session.execute(
            select(Course)
            .options(selectinload(Course.files), selectinload(Course.user))
            .filter_by(id=course_id, is_deleted=False, is_visible=True)
        )
        return q.scalars().first()

    async def show_course_with_files_paginate(self, course_id: int):
        q = (
            select(Course)
            .options(selectinload(Course.files), selectinload(Course.user))
            .filter_by(id=course_id, is_deleted=False, is_visible=True)
        )
        return q

    async def show_course_deleted(self, course_id: int):
        q = await self.db_session.execute(
            select(Course)
            .options(selectinload(Course.user))
            .filter_by(id=course_id, is_deleted=True)
        )
        return q.scalars().first()

    async def show_course_lessons(self, course_id):
        q = await self.db_session.execute(
            select(Course)
            .options(selectinload(Course.lessons), selectinload(Course.user))
            .filter_by(id=course_id, is_deleted=False, is_visible=True)
        )
        return q.scalars().first()

    async def create_course(self, request: schemas.Course, user_id: UUID4):
        new_course = Course(
            title=request.title,
            description=request.description,
            user_id=user_id,
            start_date=request.start_date,
            end_date=request.end_date,
            price=request.price,
            is_visible=True,
        )
        self.db_session.add(new_course)
        await self.db_session.flush()
        await self.db_session.refresh(new_course)
        return new_course

    async def update_course(self, course_id: int, updated_values):
        q = update(Course).where(Course.id == course_id)
        q = q.values(updated_values)
        q.execution_options(synchronize_session="fetch")
        await self.db_session.execute(q)

    async def delete_course(self, course_id: int):
        q = update(Course).where(Course.id == course_id)
        q = q.values(is_deleted=True)
        q.execution_options(synchronize_session="fetch")
        await self.db_session.execute(q)
        await self.db_session.flush()

    async def restore_course(self, course_id: int):
        q = update(Course).where(Course.id == course_id)
        q = q.values(is_deleted=False)
        q.execution_options(synchronize_session="fetch")
        await self.db_session.execute(q)

    # Category Route
    async def get_category_with_courses(self, category_id):
        q = await self.db_session.execute(
            select(Category)
            .options(selectinload(Category.courses))
            .filter_by(id=category_id)
        )
        return q.scalars().first()

    # File route
    async def get_file(self, url: str):
        q = await self.db_session.execute(select(File).filter_by(url=url))
        return q.scalars().first()

    async def create_file(self, request: FileSchema):
        new_file = File(
            title=request.title,
            description=request.description,
            url=request.url,
            duration=request.duration,
        )
        self.db_session.add(new_file)
        await self.db_session.flush()
        return new_file

    async def get_user(self, user_id):
        q = await self.db_session.execute(select(User).filter(User.id == user_id))
        return q.scalars().first()
