from typing import Optional

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from fastapi_users import models as fastapi_model
from app.auth.auth import fastapi_users
from . import schemas
from .content_dal import ContentDAL
from .dependencies import get_content_dal


router = APIRouter(tags=['Contents'])


@router.post('/core/lesson/content', status_code=201)
async def create_content(
    request: schemas.Content,
    user: fastapi_model.BaseUserDB = Depends(fastapi_users.current_user()),
    content_dal: ContentDAL = Depends(get_content_dal),
):
    if await content_dal.check_lesson_user(
        lesson_id=request.lesson_id, user_id=user.id
    ):
        new_content = await content_dal.create_content(request)
        return new_content
    return JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN,
        content={"message": "Курс вам не принадлежит"},
    )


@router.get('/core/lesson/content/{content_id}', status_code=200)
async def get_content_by_id(
    content_id: int,
    user: fastapi_model.BaseUserDB = Depends(fastapi_users.current_user()),
    content_dal: ContentDAL = Depends(get_content_dal),
):
    content = await content_dal.get_content(content_id=content_id)
    return content


@router.get('/core/lesson/{lesson_id}/contents', status_code=200)
async def get_content_of_lesson(
    lesson_id: int,
    user: fastapi_model.BaseUserDB = Depends(fastapi_users.current_user()),
    content_dal: ContentDAL = Depends(get_content_dal),
):
    contents = await content_dal.get_lesson_contents(lesson_id=lesson_id)
    return contents
