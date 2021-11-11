from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from fastapi_users import models as fastapi_model

from app.auth.auth import fastapi_users
from . import schemas

from app.file.achievement import get_achievements
from app.file.dal import FileDAL
from app.file.dependencies import get_file_dal

router = APIRouter(tags=['File'])


@router.post('/core/file/create', status_code=201)
async def create_file(
    request: schemas.File,
    user: fastapi_model.BaseUserDB = Depends(fastapi_users.current_user()),
    file_dal: FileDAL = Depends(get_file_dal),
):
    user = await file_dal.get_user_with_achievements(user.id)
    if request.course_id:
        if not await file_dal.check_course(request.course_id):
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"message": "Курс не найден"},
            )
    if request.lesson_id:
        if not await file_dal.check_lesson(request.lesson_id):
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"message": "Урок не найден"},
            )
    if request.homework_id:
        if not await file_dal.check_hw(request.homework_id):
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"message": "Домашнее задание не найдено"},
            )
    await file_dal.create_file(request, user.id)
    await get_achievements(user, file_dal)
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={"message": "Файл создан"},
    )
