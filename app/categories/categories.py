from typing import Optional

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from fastapi_pagination.ext.async_sqlalchemy import paginate
from fastapi_pagination.paginator import paginate as paginate_list
from fastapi_users import models as fastapi_model
from app.courses.schemas import CourseOut
from app.auth.auth import fastapi_users
from . import models, schemas
from .category_dal import CategoryDAL
from app.pagination import CustomPage as Page
from elastic import es
from .dependencies import get_category_dal
from http import HTTPStatus
from starlette.responses import Response

router = APIRouter(tags=['Categories'])


@router.get(
    '/core/popular_categories',
    response_model=Page[schemas.CategoryOut],
    status_code=200,
)
async def show_popular_categories(
    category_dal: CategoryDAL = Depends(get_category_dal),
):
    categories = await category_dal.get_popular_categories()
    return await paginate(category_dal.db_session, categories)


@router.get(
    '/core/categories', response_model=Page[schemas.CategoryOut], status_code=200
)
async def show_categories(
    category_dal: CategoryDAL = Depends(get_category_dal), title: Optional[str] = None
):
    categories = await category_dal.get_all_categories(title)
    return await paginate(category_dal.db_session, categories)


@router.get('/core/category/{category_id}', status_code=200)
async def show_category(
    category_id: int, category_dal: CategoryDAL = Depends(get_category_dal)
):
    category = await category_dal.get_category(category_id)
    if not category:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": "Категория не найдена"},
        )
    return category


@router.get(
    '/core/category/{category_id}/courses',
    response_model=Page[CourseOut],
    status_code=200,
)
async def show_category_courses(
    category_id: int,
    category_dal: CategoryDAL = Depends(get_category_dal),
    title: Optional[str] = None,
):
    category = await category_dal.get_category_courses(category_id)
    if not category:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": "Категория не найдена"},
        )
    if title:
        filtered_courses = [
            course for course in category.courses if course.title.startswith(title)
        ]
        return paginate_list(filtered_courses)
    return paginate_list(category.courses)


@router.post('/core/category/create', status_code=201)
async def create_category(
    request: schemas.Category,
    user: fastapi_model.BaseUserDB = Depends(
        fastapi_users.current_user(superuser=True)
    ),
    category_dal: CategoryDAL = Depends(get_category_dal),
):
    category = await category_dal.check_category_exists_by_title(request.title)
    if category:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": "Категория уже существует"},
        )
    new_category = await category_dal.create_category(
        request.image,
        request.title,
        request.description,
    )
    try:
        doc = {"title": request.title, "description": request.description}
        await es.index("categories", id=new_category.id, body=doc)
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": f"Ошибка в апдейте elastic search: {e}"},
        )
    return new_category


@router.patch('/core/category/{category_id}/update', status_code=202)
async def update_category(
    category_id: int,
    request: schemas.Category,
    user: fastapi_model.BaseUserDB = Depends(
        fastapi_users.current_user(superuser=True)
    ),
    category_dal: CategoryDAL = Depends(get_category_dal),
):
    category = await category_dal.get_category(category_id)
    if not category:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": "Категория не найдена"},
        )
    category_update = await category_dal.update_category(
        category_id, request.image, request.title, request.description
    )
    try:
        doc = {
            "doc": {
                "title": category_update.title,
                "description": category_update.description,
            }
        }
        await es.update("categories", id=category_id, body=doc)
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": f"Ошибка в апдейте elastic search: {e}"},
        )
    return category_update


@router.delete('/core/category/{category_id}', status_code=HTTPStatus.NO_CONTENT)
async def delete_category(
    category_id: int,
    user: fastapi_model.BaseUserDB = Depends(
        fastapi_users.current_user(superuser=True)
    ),
    category_dal: CategoryDAL = Depends(get_category_dal),
):
    category = await category_dal.check_category_exists_by_id(category_id)
    if not category:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": "Категория не найдена"},
        )
    await category_dal.delete_category(category_id)
    try:
        await es.delete(index="categories", id=category_id)
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": f"Ошибка в апдейте elastic search: {e}"},
        )
    return Response(status_code=204)
