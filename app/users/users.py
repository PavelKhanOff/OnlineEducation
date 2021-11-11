import uuid
from typing import Any, Optional

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from fastapi_pagination.ext.async_sqlalchemy import paginate
from fastapi_pagination.paginator import paginate as paginate_list
from fastapi_users import models as fastapi_model
from sqlalchemy.ext.asyncio.result import AsyncResult
from http import HTTPStatus
from starlette.responses import Response
from pydantic import UUID4

from app.achievements.schemas import AchievementOut
from app.auth.auth import fastapi_users
from app.courses.schemas import MyCourseOut
from app.pagination import CustomPage as Page
from . import models, schemas
from .user_dal import UserDAL
from .dependencies import get_user_dal
from app.follows.follow_dal import FollowDAL
from app.follows.dependencies import get_follow_dal


router = APIRouter(tags=['User'])


@router.get("/core/users", response_model=Page[schemas.UserOut], status_code=200)
async def get_users(
    user_dal: UserDAL = Depends(get_user_dal), username: Optional[str] = None
):
    users = await user_dal.get_users(username)
    return paginate_list(users)


@router.get(
    "/core/popular_authors", response_model=Page[schemas.UserOut], status_code=200
)
async def get_popular_authors(user_dal: UserDAL = Depends(get_user_dal)):
    users = await user_dal.get_popular_authors()
    return paginate_list(users)


@router.get('/core/user/{user_id}', response_model=schemas.UserOut, status_code=200)
async def get_user(
    user_id: UUID4,
    user_dal: UserDAL = Depends(get_user_dal),
    follow_dal: FollowDAL = Depends(get_follow_dal),
    user: fastapi_model.BaseUserDB = Depends(fastapi_users.current_user()),
):
    second_user = await user_dal.get_user(user_id)
    if not second_user:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": "Пользователь не найден"},
        )
    follow = await follow_dal.follow_exists(
        user_id=user.id, second_user_id=second_user.id
    )
    if follow:
        second_user.is_followed = True
    else:
        second_user.is_followed = False

    return second_user


@router.get('/core/user/check/username')
async def check_username(username: str, user_dal: UserDAL = Depends(get_user_dal)):
    return await user_dal.check_username(username)


@router.delete('/core/user/{user_id}/delete', status_code=HTTPStatus.NO_CONTENT)
async def delete_user(
    user_id: UUID4,
    user: fastapi_model.BaseUserDB = Depends(
        fastapi_users.current_user(superuser=True)
    ),
    user_dal: UserDAL = Depends(get_user_dal),
):
    user = await user_dal.get_user(user_id)
    if not user:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": "Пользователь не найден"},
        )
    await user_dal.delete_user(user_id)
    return Response(status_code=204)


@router.patch(
    '/core/user/{user_id}/update/', response_model=schemas.UserOut, status_code=202
)
async def update_user(
    request: schemas.UserUpdateSecond,
    user_id: UUID4,
    user: fastapi_model.BaseUserDB = Depends(fastapi_users.current_user()),
    user_dal: UserDAL = Depends(get_user_dal),
):
    check_admin = await user_dal.get_user(user.id)
    if user.id != user_id:
        if check_admin.is_superuser is False:
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={"message": "Запрещено"},
            )
    user = await user_dal.get_user(user_id)
    check_user_exists = await user_dal.get_user_by_username(request.username)
    if check_user_exists and check_user_exists.id != user_id:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": "Пользователь с таким username уже существует"},
        )
    if not user:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": "Пользователь не найден"},
        )
    await user_dal.update_user(
        user_id,
        request.username,
        request.first_name,
        request.last_name,
        request.email,
        request.description,
        request.website,
        request.phone,
        request.gender,
        request.birth_date,
    )
    user = await user_dal.get_user(user_id)
    return user


@router.get(
    '/core/user/{user_id}/achievements',
    response_model=Page[AchievementOut],
    status_code=200,
)
async def show_user_achievements(
    user_id: UUID4,
    user_dal: UserDAL = Depends(get_user_dal),
    title: Optional[str] = None,
):
    user = await user_dal.get_user(user_id)
    if not user:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": "Пользователь не найден"},
        )
    if title:
        filtered_ach = [ach for ach in user.achievements if ach.title.startswith(title)]
        return paginate_list(filtered_ach)
    return paginate_list(user.achievements)


@router.get(
    '/core/user/{user_id}/followers',
    response_model=Page[schemas.UserOut],
    status_code=200,
)
async def show_user_followers(
    user_id: UUID4,
    user_dal: UserDAL = Depends(get_user_dal),
    username: Optional[str] = None,
    auth_user: fastapi_model.BaseUserDB = Depends(
        fastapi_users.current_user(optional=True)
    ),
    follow_dal: FollowDAL = Depends(get_follow_dal),
):
    user = await user_dal.get_user_followers(user_id)
    if not user:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": "Пользователь не найден"},
        )
    if auth_user:
        for follower in user.followers:
            follow = await follow_dal.follow_exists(
                user_id=auth_user.id, second_user_id=follower.id
            )
            if follow:
                follower.is_followed = True
            else:
                follower.is_followed = False
    if username:
        filtered_users = [
            ach for ach in user.followers if ach.username.startswith(username)
        ]
        return paginate_list(filtered_users)
    return paginate_list(user.followers)


@router.get(
    '/core/user/{user_id}/following',
    response_model=Page[schemas.UserOut],
    status_code=200,
)
async def show_user_following(
    user_id: UUID4,
    user_dal: UserDAL = Depends(get_user_dal),
    username: Optional[str] = None,
    auth_user: fastapi_model.BaseUserDB = Depends(
        fastapi_users.current_user(optional=True)
    ),
    follow_dal: FollowDAL = Depends(get_follow_dal),
):
    user = await user_dal.get_user_following(user_id)
    if not user:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": "Пользователь не найден"},
        )
    if auth_user:
        for followings in user.following:
            follow = await follow_dal.follow_exists(
                user_id=auth_user.id, second_user_id=followings.id
            )
            if follow:
                followings.is_followed = True
            else:
                followings.is_followed = False
    if username:
        filtered_users = [
            ach for ach in user.following if ach.username.startswith(username)
        ]
        return paginate_list(filtered_users)

    return paginate_list(user.following)


@router.get(
    '/core/user/{user_id}/courses', response_model=Page[MyCourseOut], status_code=200
)
async def show_user_courses(
    user_id: UUID4,
    user_dal: UserDAL = Depends(get_user_dal),
    title: Optional[str] = None,
):
    user = await user_dal.get_user_courses(user_id)
    if not user:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": "Пользователь не найден"},
        )
    if title:
        filtered_courses = [
            course for course in user.courses if course.title.startswith(title)
        ]
        return paginate_list(filtered_courses)
    return paginate_list(user.courses)


@router.get('/core/user/courses/my', response_model=Page[MyCourseOut], status_code=200)
async def show_my_courses(
    user: fastapi_model.BaseUserDB = Depends(fastapi_users.current_user()),
    user_dal: UserDAL = Depends(get_user_dal),
):
    courses = await user_dal.get_courses(user.id)
    if not user:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": "Пользователь не найден"},
        )
    return await paginate(user_dal.db_session, courses)


@router.get('/core/user/courses/followed', response_model=Page[MyCourseOut], status_code=200)
async def show_my_followed_courses(
    user: fastapi_model.BaseUserDB = Depends(fastapi_users.current_user()),
    user_dal: UserDAL = Depends(get_user_dal),
):
    user_with_courses = await user_dal.get_user_with_sub_course(user.id)
    if not user:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": "Пользователь не найден"},
        )
    print(111111111111111111111111111111111111111111, user_with_courses.subscribed_courses)
    return paginate_list(user_with_courses.subscribed_courses)


@router.get(
    '/core/user/courses/my/deleted', response_model=Page[MyCourseOut], status_code=200
)
async def show_my_deleted_courses(
    user: fastapi_model.BaseUserDB = Depends(fastapi_users.current_user()),
    user_dal: UserDAL = Depends(get_user_dal),
):
    courses = await user_dal.get_deleted_courses(user.id)
    if not user:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": "Пользователь не найден"},
        )
    return await paginate(user_dal.db_session, courses)


@router.post('/core/user/author/')
async def author(
    user: fastapi_model.BaseUserDB = Depends(fastapi_users.current_user()),
    user_dal: UserDAL = Depends(get_user_dal),
):
    is_author = not user.is_author
    await user_dal.author(user.id, is_author)
    if is_author:
        message = "Вы стали автором"
    else:
        message = "Вы перестали быть автором"
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": message},
    )


@router.get(
    '/core/createsuperuser',
    tags=["Superuser"],
    include_in_schema=False,
    status_code=200,
)
async def create_superuser(user_dal: UserDAL = Depends(get_user_dal)):
    new_user = await user_dal.create_superuser()
    return new_user
