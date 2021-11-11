# from app.database import SessionLocal
from elastic import es
from fastapi.responses import JSONResponse
from fastapi import APIRouter, Depends, status
from fastapi_users import models as fastapi_model
from app.auth.auth import fastapi_users
from app.users.models import User as UserModel
from app.courses.models import Course
from app.lessons.models import Lesson
from app.achievements.models import Achievement
from app.categories.models import Category

router = APIRouter(tags=['additional_functions'])

#
# @router.get('/core/additional_functions/sql_to_document')
# def sql_to_document(user: fastapi_model.BaseUserDB = Depends(fastapi_users.current_user())):
#     db = SessionLocal()
#     user = db.query(UserModel).filter(UserModel.id == user.id).first()
#     if not user:
#         return JSONResponse(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             content={"message": "Пользователя не существует"},
#         )
#     if user.is_superuser is False:
#         return JSONResponse(
#             status_code=status.HTTP_403_FORBIDDEN,
#             content={"message": "Запрещено"},
#         )
#     users = db.query(UserModel).all()
#     for user in users:
#         doc = {
#             "username": user.username,
#             "email": user.email,
#             "first_name": user.first_name,
#             "last_name": user.last_name,
#             "achievements": [ach.id for ach in user.achievements],
#         }
#         es.index(index="users", id=user.id, body=doc)
#     courses = db.query(Course).all()
#     for course in courses:
#         category = []
#         if course.category_obj:
#             category = [ctg.id for ctg in course.category_obj]
#         doc = {
#             "title": course.title,
#             "description": course.description,
#             "author": course.user,
#             "category": category,
#             "is_deleted": False,
#         }
#         es.index(index="courses", id=course.id, body=doc)
#     lessons = db.query(Lesson).all()
#     for lesson in lessons:
#         doc = {
#             "title": lesson.title,
#             "description": lesson.description,
#             "estimated_time": lesson.estimated_time,
#             "course_id": lesson.course_id,
#             "tags": [tag.title for tag in lesson.tags],
#         }
#         es.index(index="lessons", id=lesson.id, body=doc)
#     achievements = db.query(Achievement).all()
#     for achievement in achievements:
#         doc = {
#             "title": achievement.title,
#             "description": achievement.description,
#         }
#         es.index(index="achievements", id=achievement.id, body=doc)
#     categories = db.query(Category).all()
#     for category in categories:
#         doc = {"title": category.title, "description": category.description}
#         es.index(index="categories", id=category.id, body=doc)
#     return JSONResponse(
#         status_code=status.HTTP_200_OK,
#         content={"message": "DONE"},
#     )
