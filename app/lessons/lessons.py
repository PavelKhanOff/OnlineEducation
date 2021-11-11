from typing import Optional

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from fastapi_pagination.paginator import paginate as paginate_list
from fastapi_users import models as fastapi_model
from app.auth.auth import fastapi_users
from . import schemas
from app.pagination import CustomPage as Page
from elastic import es
from app.homework.schemas import HomeworkOut
from .lesson_dal import LessonDAL
from .dependencies import get_lesson_dal
from .additional_functions import send_lesson_notifications
from http import HTTPStatus
from starlette.responses import Response


router = APIRouter(tags=['Lesson'])


@router.get('/core/lesson/{lesson_id}', status_code=200)
async def show_lesson(lesson_id: int, lesson_dal: LessonDAL = Depends(get_lesson_dal)):
    lesson = await lesson_dal.get_lesson(lesson_id)
    if not lesson:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": "Такой урок не найден"},
        )
    return lesson


@router.post('/core/lesson/create', status_code=201)
async def create_lesson(
    request: schemas.Lesson,
    user: fastapi_model.BaseUserDB = Depends(fastapi_users.current_user()),
    lesson_dal: LessonDAL = Depends(get_lesson_dal),
):
    course = await lesson_dal.get_course(request.course_id)
    if not course:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": "Такой курс не найден"},
        )
    if not await lesson_dal.check_course_exists(user.id, request.course_id):
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"message": "Курс вам не принадлежит"},
        )
    new_lesson = await lesson_dal.create_lesson(
        request.title, request.description, request.estimated_time, request.course_id
    )
    await send_lesson_notifications(user.id, course.title)
    try:
        doc = {
            "title": request.title,
            "description": request.description,
            "estimated_time": request.estimated_time,
            "course_id": request.course_id,
            "tags": [],
        }
        await es.index("lessons", id=new_lesson.id, body=doc)
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": f"Ошибка в апдейте elastic search: {e}"},
        )
    return new_lesson


@router.patch('/core/lesson/{lesson_id}/update', status_code=202)
async def update_lesson(
    request: schemas.UpdateLesson,
    lesson_id: int,
    user: fastapi_model.BaseUserDB = Depends(fastapi_users.current_user()),
    lesson_dal: LessonDAL = Depends(get_lesson_dal),
):
    lesson = await lesson_dal.check_lesson_exists(lesson_id)
    if not lesson:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": "Такой урок не найден"},
        )
    if await lesson_dal.check_course_exists(user.id, request.course_id):
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"message": "Вы не можете редактировать этот урок"},
        )
    lesson = await lesson_dal.update_lesson(
        lesson_id, request.title, request.description, request.estimated_time
    )
    try:
        doc = {
            "doc": {
                "title": lesson.title,
                "description": lesson.description,
                "estimated_time": lesson.estimated_time,
            }
        }
        await es.update("lessons", id=lesson_id, body=doc)
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": f"Ошибка в апдейте elastic search: {e}"},
        )
    return lesson


@router.delete('/core/lesson/{lesson_id}/delete', status_code=HTTPStatus.NO_CONTENT)
async def delete_lesson(
    lesson_id: int,
    user: fastapi_model.BaseUserDB = Depends(fastapi_users.current_user()),
    lesson_dal: LessonDAL = Depends(get_lesson_dal),
):
    lesson = await lesson_dal.get_lesson_with_course_id(lesson_id)
    if not lesson:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": "Урок не существует"},
        )
    user = await lesson_dal.get_user_courses(user.id)
    if lesson.course_id not in [course.id for course in user.courses]:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"message": "Вы не можете удалить этот урок"},
        )
    deletion = await lesson_dal.delete_lesson(lesson_id)
    try:
        await es.delete("lessons", id=lesson.id)
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": f"Ошибка в апдейте elastic search: {e}"},
        )
    return Response(status_code=204)


@router.get('/core/lesson/{lesson_id}/course', status_code=200)
async def show_lessons_course(
    lesson_id: int, lesson_dal: LessonDAL = Depends(get_lesson_dal)
):
    lesson = await lesson_dal.get_lesson_with_course_id(lesson_id)
    if not lesson:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": "Урок не существует"},
        )
    course = await lesson_dal.get_course(lesson.course_id)
    if not course:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": "Курса не существует"},
        )
    return course


@router.get(
    '/core/lesson/{lesson_id}/homework',
    response_model=Page[HomeworkOut],
    status_code=200,
)
async def show_lessons_homework(
    lesson_id: int,
    lesson_dal: LessonDAL = Depends(get_lesson_dal),
    title: Optional[str] = None,
):
    lesson = await lesson_dal.get_lesson_with_homework(lesson_id)
    if not lesson:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": "Урок не найден"},
        )
    if title:
        filtered_homework = [
            homework for homework in lesson.homework if homework.title.startswith(title)
        ]
        return paginate_list(filtered_homework)
    return paginate_list(lesson.homework)


@router.post('/core/tag/add', status_code=200)
async def add_tag_to_lesson(
    request: schemas.AddTag,
    user: fastapi_model.BaseUserDB = Depends(fastapi_users.current_user()),
    lesson_dal: LessonDAL = Depends(get_lesson_dal),
):
    lesson = await lesson_dal.get_lesson_with_course_id(request.lesson_id)
    if not lesson:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": "Урок не найден"},
        )
    course = await lesson_dal.get_course(lesson.course_id)
    if not course:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": "Курс урока не найден"},
        )
    if user.id != course.user_id:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"message": "У вас нет прав на это действие"},
        )
    tag = await lesson_dal.get_tag(request.tag_id)
    if not tag:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": "Тэг не найден"},
        )
    lesson = await lesson_dal.get_lesson_with_tags(request.lesson_id)
    if tag in lesson.tags:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": "Тэг уже привязан"},
        )
    lesson.tags.append(tag)
    try:
        doc = {
            "script": {
                "source": "ctx._source.tags.add(params.tag)",
                "lang": "painless",
                "params": {"tag": tag.title},
            }
        }
        await es.update("lessons", id=request.lesson_id, body=doc)
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": f"Ошибка в апдейте elastic search: {e}"},
        )
    return JSONResponse(content={"message": "Успешно привязано"})


@router.delete('/core/tag/delete', status_code=HTTPStatus.NO_CONTENT)
async def unbound_tag_to_lesson(
    request: schemas.AddTag,
    user: fastapi_model.BaseUserDB = Depends(fastapi_users.current_user()),
    lesson_dal: LessonDAL = Depends(get_lesson_dal),
):
    lesson = await lesson_dal.get_lesson_with_course_id(request.lesson_id)
    course = await lesson_dal.get_course(lesson.course_id)
    if not course:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": "Курс урока не найден"},
        )
    if not lesson:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": "Урок не найден"},
        )
    if user.id != course.user:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"message": "У вас нет прав на это действие"},
        )
    tag = await lesson_dal.get_tag(request.tag_id)
    if not tag:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": "Тэг не найден"},
        )
    lesson = await lesson_dal.get_lesson(request.lesson_id)
    if tag not in lesson.tags:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": "Тэг не был привязан к уроку"},
        )
    lesson.tags.remove(tag)
    try:
        body_script = {
            "script": {
                "source": "if (ctx._source.tags.contains(params.tag)) { ctx._source.tags.remove(ctx._source.tags.indexOf(params.tag)) }",
                "lang": "painless",
                "params": {"tag": tag.title},
            }
        }
        await es.update("lessons", id=request.lesson_id, body=body_script)
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": f"Ошибка в апдейте elastic search: {e}"},
        )
    return Response(status_code=204)
