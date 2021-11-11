from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from fastapi_users import models as fastapi_model
from app.pagination import CustomPage as Page
from fastapi_pagination.paginator import paginate as paginate_list
from app.auth.auth import fastapi_users

from http import HTTPStatus
from starlette.responses import Response
from . import schemas

from app.file.schemas import FileToHomework
from app.homework.dal import HomeWorkDAL
from app.homework.dependencies import get_homework_dal


router = APIRouter(tags=['Homework'])


@router.get('/core/homework/{homework_id}', status_code=200)
async def show_homework(
    homework_id: int, homework_dal: HomeWorkDAL = Depends(get_homework_dal)
):
    homework = await homework_dal.get_hw(homework_id)
    if not homework:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": "Домашнее задание не найдено"},
        )
    return homework


@router.post('/core/homework/create', status_code=201)
async def create_homework(
    request: schemas.Homework,
    user: fastapi_model.BaseUserDB = Depends(fastapi_users.current_user()),
    homework_dal: HomeWorkDAL = Depends(get_homework_dal),
):
    lesson_course_id = await homework_dal.get_lesson(request.lesson_id)
    if not lesson_course_id:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": "Урок не найден"},
        )
    if await homework_dal.check_course_exists(user.id, lesson_course_id):
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"message": "Домашнее задание вам не принадлежит"},
        )
    return await homework_dal.create_hw(request)


@router.patch('/core/homework/{homework_id}/update', status_code=202)
async def update_homework(
    homework_id: int,
    request: schemas.UpdateHomework,
    user: fastapi_model.BaseUserDB = Depends(fastapi_users.current_user()),
    homework_dal: HomeWorkDAL = Depends(get_homework_dal),
):
    homework = await homework_dal.check_hw(homework_id)
    if not homework:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": "Домашнее задание не найдено"},
        )
    lesson_course_id = await homework_dal.get_lesson(homework.lesson_id)
    if await homework_dal.check_course_exists(user.id, lesson_course_id):
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"message": "Домашнее задание вам не принадлежит"},
        )
    await homework_dal.update_hw(homework_id, request.dict(exclude_unset=True))
    return homework


@router.patch('/core/homework/{homework_id}/add_file', status_code=202)
async def add_file_to_homework(
    homework_id: int,
    request: FileToHomework,
    user: fastapi_model.BaseUserDB = Depends(fastapi_users.current_user()),
    homework_dal: HomeWorkDAL = Depends(get_homework_dal),
):
    homework = await homework_dal.get_hw_with_files(homework_id)
    if not homework:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": "Домашнего задания не существует"},
        )
    lesson_course_id = await homework_dal.get_lesson(homework.lesson_id)
    if not lesson_course_id:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": "Урока не существует"},
        )
    if await homework_dal.check_course_exists(user.id, lesson_course_id):
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"message": "Домашнее задание вам не принадлежит"},
        )
    new_file = await homework_dal.create_file(request)
    homework.files.append(new_file)
    await homework_dal.db_session.flush()
    return JSONResponse(content={"message": "Файл успешно добавлен"})


@router.patch(
    '/core/homework/{homework_id}/files',
    response_model=Page[schemas.FileOut],
    status_code=202,
)
async def show_homework_files(
    homework_id: int,
    homework_dal: HomeWorkDAL = Depends(get_homework_dal),
):
    homework_with_files = await homework_dal.get_hw_with_files(homework_id)
    if not homework_with_files:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": "Урока не существует"},
        )
    return paginate_list(homework_with_files.files)


@router.delete('/core/homework/{homework_id}', status_code=HTTPStatus.NO_CONTENT)
async def delete_homework(
    homework_id: int,
    user: fastapi_model.BaseUserDB = Depends(fastapi_users.current_user()),
    homework_dal: HomeWorkDAL = Depends(get_homework_dal),
):
    homework = await homework_dal.check_hw(homework_id)
    if not homework:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": "Домашнее задание не существует"},
        )
    lesson_course_id = await homework_dal.get_lesson(homework.lesson_id)
    if await homework_dal.check_course_exists(user.id, lesson_course_id):
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"message": "Домашнее задание вам не принадлежит"},
        )
    await homework_dal.delete_hw(homework_id)
    return Response(status_code=204)


@router.get('/core/homework/{homework_id}/lesson', status_code=200)
async def get_homework_lesson(
    homework_id: int, homework_dal: HomeWorkDAL = Depends(get_homework_dal)
):
    homework = await homework_dal.get_hw(homework_id)
    if not homework:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": "Домашнее задание не найдено"},
        )
    homework_lesson = await homework_dal.get_lesson(homework.lesson_id)
    if not homework_lesson:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": "Урок не найден"},
        )
    return homework_lesson
