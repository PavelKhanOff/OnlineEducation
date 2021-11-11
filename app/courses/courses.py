from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from fastapi_pagination.paginator import paginate as paginate_list
from fastapi_users import models as fastapi_model
from http import HTTPStatus
from starlette.responses import Response
from app.auth.auth import fastapi_users
from . import schemas
from .additional_functions import send_course_notifications
from app.pagination import CustomPage as Page
from elastic import es
from app.lessons.schemas import LessonOut, FileOut
from app.file.schemas import FileToCourse
from app.courses.course_dal import CourseDAL
from app.courses.dependencies import get_course_dal


router = APIRouter(tags=['Courses'])


@router.get('/core/courses', response_model=Page[schemas.CourseOut], status_code=200)
async def show_all_courses(
    course_dal: CourseDAL = Depends(get_course_dal), title: Optional[str] = None
):
    courses = await course_dal.show_all_courses(title)
    return paginate_list(courses)


@router.get('/core/courses/{course_id}', status_code=200)
async def show_course(course_id: int, course_dal: CourseDAL = Depends(get_course_dal)):
    course = await course_dal.show_course_with_lessons(course_id)
    if not course:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": "Такого курса не существует"},
        )
    return course


@router.post('/core/course/create', response_model=schemas.MyCourseOut, status_code=201)
async def create_course(
    request: schemas.Course,
    user: fastapi_model.BaseUserDB = Depends(fastapi_users.current_user()),
    course_dal: CourseDAL = Depends(get_course_dal),
):
    if user.is_author is False:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": "Вы не являетесь автором"},
        )
    # if (
    #     request.start_date <= datetime.now()
    #     or request.end_date <= datetime.now()
    #     or request.start_date >= request.end_date
    # ):
    #     return JSONResponse(
    #         status_code=status.HTTP_400_BAD_REQUEST,
    #         content={"message": "Введите корректную дату"},
    #     )
    new_course = await course_dal.create_course(request, user.id)
    await send_course_notifications(user.id)
    try:
        doc = {
            "title": request.title,
            "description": request.description,
            "author": user.id,
            "category": [],
            "is_deleted": False,
        }
        await es.index("courses", id=new_course.id, body=doc)
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": f"Ошибка в апдейте elastic search: {e}"},
        )
    return await course_dal.get_course(course_id=new_course.id)


@router.get('/core/course/{course_id}/category', status_code=200)
async def show_course_category(
    course_id: int, course_dal: CourseDAL = Depends(get_course_dal)
):
    course = await course_dal.show_course(course_id)
    if not course:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": "Курс не найден"},
        )
    category = await course_dal.show_category(course.category)
    if not category:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": "Категория не найдена"},
        )
    return category


@router.get(
    '/core/course/{course_id}/lessons',
    response_model=Page[LessonOut],
    status_code=200,
)
async def show_course_lessons(
    course_id: int,
    course_dal: CourseDAL = Depends(get_course_dal),
    title: Optional[str] = None,
):
    course = await course_dal.show_course_lessons(course_id)
    if not course:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": "Курс не найден"},
        )
    if title:
        filtered_lessons = [
            lesson for lesson in course.lessons if lesson.title.startswith(title)
        ]
        return paginate_list(filtered_lessons)
    return paginate_list(course.lessons)


@router.patch(
    '/core/course/{course_id}/update',
    response_model=schemas.UpdateCourse,
    status_code=202,
)
async def update_course(
    course_id: int,
    request: schemas.UpdateCourse,
    user: fastapi_model.BaseUserDB = Depends(fastapi_users.current_user()),
    course_dal: CourseDAL = Depends(get_course_dal),
):
    course = await course_dal.show_course(course_id)
    if not course:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": "Курс не найден"},
        )
    if user.id != course.user_id:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"message": "У вас нет прав на это действие"},
        )
    # if request.start_date is not None:
    #     if (
    #         request.start_date <= datetime.now()
    #         or course.end_date <= datetime.now()
    #         or request.start_date >= course.end_date
    #     ):
    #         return JSONResponse(
    #             status_code=status.HTTP_400_BAD_REQUEST,
    #             content={"message": "Введите корректную дату"},
    #         )
    # if request.end_date is not None:
    #     if (
    #         course.start_date <= datetime.now()
    #         or request.end_date <= datetime.now()
    #         or course.start_date >= request.end_date
    #     ):
    #         return JSONResponse(
    #             status_code=status.HTTP_400_BAD_REQUEST,
    #             content={"message": "Введите корректную дату"},
    #         )
    # if request.end_date is not None and request.start_date is not None:
    #     if (
    #         request.start_date <= datetime.now()
    #         or request.end_date <= datetime.now()
    #         or request.start_date >= request.end_date
    #     ):
    #         return JSONResponse(
    #             status_code=status.HTTP_400_BAD_REQUEST,
    #             content={"message": "Введите корректную дату"},
    #         )
    await course_dal.update_course(course_id, request.dict(exclude_unset=True))
    try:
        doc = {"doc": {"title": request.title, "description": request.description}}
        await es.update("courses", id=course_id, body=doc)
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": f"Ошибка в апдейте elastic search: {e}"},
        )
    return course


@router.delete('/core/course/{course_id}', status_code=HTTPStatus.NO_CONTENT)
async def delete_course(
    course_id: int,
    user: fastapi_model.BaseUserDB = Depends(fastapi_users.current_user()),
    course_dal: CourseDAL = Depends(get_course_dal),
):
    course = await course_dal.show_course(course_id)
    if course is None:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": "Курс не найден"},
        )
    if user.id != course.user_id:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"message": "У вас нет прав на это действие"},
        )
    if course.is_deleted is True:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": "Курс уже был удален"},
        )
    await course_dal.delete_course(course_id)
    try:
        body = {"doc": {'is_deleted': True}}
        await es.update("courses", id=course.id, body=body)
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": f"Ошибка в апдейте elastic search: {e}"},
        )
    return Response(status_code=204)


@router.post('/core/course/visible')
async def hide_or_expose(
    course_id: int,
    user: fastapi_model.BaseUserDB = Depends(fastapi_users.current_user()),
    course_dal: CourseDAL = Depends(get_course_dal),
):
    course = await course_dal.get_course(course_id)
    if not course:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": "Курс не найден"},
        )

    if user.id != course.user_id:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"message": "У вас нет прав на это действие"},
        )
    if course.is_visible:
        course.is_visible = False
        return JSONResponse(
            status_code=status.HTTP_200_OK, content={"message": "Your course is hided"}
        )
    else:
        course.is_visible = True
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": "Your course is visible"},
        )


@router.get('/core/course/{course_id}/restore')
async def restore_course(
    course_id: int,
    user: fastapi_model.BaseUserDB = Depends(fastapi_users.current_user()),
    course_dal: CourseDAL = Depends(get_course_dal),
):
    course = await course_dal.show_course_deleted(course_id)
    if not course:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": "Курс не найден"},
        )

    if user.id != course.user_id:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"message": "У вас нет прав на это действие"},
        )
    await course_dal.restore_course(course_id)
    try:
        body = {"doc": {'is_deleted': False}}
        await es.update("courses", id=course.id, body=body)
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": f"Ошибка в апдейте elastic search: {e}"},
        )
    return 'Восстановлено успешно'


@router.post('/core/category/add', status_code=201)
async def add_category_to_course(
    request: schemas.AddCategory,
    user: fastapi_model.BaseUserDB = Depends(fastapi_users.current_user()),
    course_dal: CourseDAL = Depends(get_course_dal),
):
    course = await course_dal.show_course(request.course_id)
    if not course:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": "Курс не найден"},
        )
    if user.id != course.user_id:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"message": "У вас нет прав на это действие"},
        )

    category = await course_dal.get_category_with_courses(request.category_id)
    if not category:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": "Категория не найдена"},
        )
    category.courses.append(course)
    await course_dal.db_session.flush()
    try:
        body = {
            "script": {
                "source": "ctx._source.category.add(params.category)",
                "lang": "painless",
                "params": {"category": category.id},
            }
        }
        await es.update("courses", id=course.id, body=body)
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": f"Ошибка в апдейте elastic search: {e}"},
        )
    return JSONResponse(content={"message": "Успешно привязано"})


@router.patch('/core/course/{course_id}/add_file', status_code=202)
async def add_file_to_course(
    request: FileToCourse,
    course_id: int,
    user: fastapi_model.BaseUserDB = Depends(fastapi_users.current_user()),
    course_dal: CourseDAL = Depends(get_course_dal),
):
    course = await course_dal.show_course_with_files(course_id)
    if not course:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"message": "Такого курса не существует"},
        )
    if user.id != course.user_id:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"message": "У вас нет прав на это действие"},
        )
    if await course_dal.get_file(request.url):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": "Файл с таким юрлом уже существует"},
        )
    new_file = await course_dal.create_file(request)
    course.files.append(new_file)
    await course_dal.db_session.flush()
    return JSONResponse(content={"message": "Успешно привязано"})


@router.patch(
    '/core/course/{course_id}/files', response_model=Page[FileOut], status_code=200
)
async def show_courses_files(
    course_id: int,
    course_dal: CourseDAL = Depends(get_course_dal),
):
    course = await course_dal.show_course_with_files(course_id)
    if not course:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"message": "Такого курса не существует"},
        )
    return paginate_list(course.files)
