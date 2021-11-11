from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from fastapi_users import models as fastapi_model
from app.auth.auth import fastapi_users
from . import schemas
from .additional_functions import send_follow_notifications, add_achievements
from redis_conf.redis import redis_cache
from app.follows.follow_dal import FollowDAL
from app.follows.dependencies import get_follow_dal

router = APIRouter(tags=['Follow'])


@router.post('/core/follow')
async def follow(
    request: schemas.Follow,
    user: fastapi_model.BaseUserDB = Depends(fastapi_users.current_user()),
    follow_dal: FollowDAL = Depends(get_follow_dal),
):

    author_username = await follow_dal.get_username(request.author_id)

    if not user or not author_username:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": "Юзер или автор не найдены"},
        )
    checker = await follow_dal.follow(user.id, request.author_id)
    if checker:
        message = "подписался на"
        await send_follow_notifications(user.id, request.author_id)
    else:
        message = "отписался от"
    await follow_dal.db_session.flush()
    user_followers_count = await follow_dal.user_followers_count(user.id)
    user_following_count = await follow_dal.user_following_count(user.id)
    author_followers_count = await follow_dal.user_followers_count(request.author_id)
    author_following_count = await follow_dal.user_following_count(request.author_id)
    await redis_cache.hset(
        f"user:{user.id}",
        mapping={
            "followers_count": user_followers_count,
            "following_count": user_following_count,
        },
    )
    await redis_cache.hset(
        f"user:{request.author_id}",
        mapping={
            "followers_count": author_followers_count,
            "following_count": author_following_count,
        },
    )
    await add_achievements(request.author_id, follow_dal)
    return JSONResponse(
        content={"message": f'{user.username} {message } {author_username}'}
    )
