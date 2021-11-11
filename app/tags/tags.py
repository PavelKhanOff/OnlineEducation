from typing import Optional

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from fastapi_pagination.ext.async_sqlalchemy import paginate
from fastapi_users import models as fastapi_model
from http import HTTPStatus
from starlette.responses import Response

from app.auth.auth import fastapi_users

from app.pagination import CustomPage as Page
from . import schemas
from elastic import es

from app.tags.tag_dal import TagDAL
from app.tags.dependencies import get_tag_dal


router = APIRouter(tags=['Tags'])


@router.get('/core/tags', response_model=Page[schemas.TagOut], status_code=200)
async def show_tags(
    tag_dal: TagDAL = Depends(get_tag_dal), title: Optional[str] = None
):
    tags = await tag_dal.get_all_query()
    if title:
        tags = await tag_dal.get_by_title_query(title)
    return await paginate(tag_dal.db_session, tags)


@router.get('/core/tag/{tag_id}', response_model=schemas.TagOut, status_code=200)
async def show_tag(tag_id: int, tag_dal: TagDAL = Depends(get_tag_dal)):
    tag = await tag_dal.get_by_id(tag_id)
    if not tag:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": "Тэг не найден"},
        )
    return tag


@router.post('/core/tag/create', status_code=201)
async def create_tag(
    request: schemas.TagOut,
    user: fastapi_model.BaseUserDB = Depends(
        fastapi_users.current_user(superuser=True)
    ),
    tag_dal: TagDAL = Depends(get_tag_dal),
):
    if await tag_dal.get_by_title(request.title):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": "Тэг уже существует"},
        )
    new_tag = await tag_dal.create_tag(request.title)
    return new_tag


@router.patch('/core/tag/{tag_id}/update', status_code=202)
async def update_tag(
    tag_id: int,
    request: schemas.TagOut,
    user: fastapi_model.BaseUserDB = Depends(
        fastapi_users.current_user(superuser=True)
    ),
    tag_dal: TagDAL = Depends(get_tag_dal),
):
    tag = await tag_dal.get_by_id(tag_id)
    if not tag:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": "Тэг не найден"},
        )
    await tag_dal.update_tag(tag_id, request.dict(exclude_unset=True))
    return tag


@router.delete('/core/tag/{tag_id}/delete', status_code=HTTPStatus.NO_CONTENT)
async def delete_tag(
    tag_id: int,
    user: fastapi_model.BaseUserDB = Depends(
        fastapi_users.current_user(superuser=True)
    ),
    tag_dal: TagDAL = Depends(get_tag_dal),
):
    tag = await tag_dal.get_by_id(tag_id)
    if not tag:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": "Тэг не найден"},
        )
    await tag_dal.delete_tag(tag_id)
    try:
        doc = {
            "script": {
                "source": "if (ctx._source.tags.contains(params.tag)) { ctx._source.tags.rem"
                "ove(ctx._source.tags.indexOf(params.tag)) }",
                "lang": "painless",
                "params": {"tag": tag.title},
            },
            "query": {"match": {"tags": tag.title}},
        }
        await es.update_by_query("lessons", body=doc)
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": f"Ошибка в апдейте elastic search: {e}"},
        )
    return Response(status_code=204)
