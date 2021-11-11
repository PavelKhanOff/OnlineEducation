from typing import Any, Dict

import databases
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi_users import FastAPIUsers
from fastapi_users.authentication import JWTAuthentication

from app.config import SECRET, SQLALCHEMY_DATABASE_URL_USERS
from app.auth.fastapi_users_changed import (
    OverridenSQLAlchemyUserDatabase,
    get_auth_router,
    get_register_router,
    get_users_router,
    get_verify_router,
    get_verify_token,
)
from app.helper_functions import validate_password
from app.users import models, schemas
from elastic import es
from redis_conf.redis import redis_cache
from app.email.send_emails import send_register_mail


users = models.User.__table__
database = databases.Database(SQLALCHEMY_DATABASE_URL_USERS)
user_db = OverridenSQLAlchemyUserDatabase(schemas.UserDB, database, users)


jwt_authentication = JWTAuthentication(
    secret=SECRET, lifetime_seconds=30 * 24 * 60 * 60, tokenUrl="/core/auth/login"
)

fastapi_users = FastAPIUsers(
    user_db,
    [jwt_authentication],
    schemas.User,
    schemas.UserCreate,
    schemas.UserUpdate,
    schemas.UserDB,
    validate_password=validate_password,
)


async def on_after_register(user: schemas.UserDB, request: Request):
    token = await get_verify_token(
        user.email, fastapi_users.get_user, jwt_authentication.secret
    )
    await send_register_mail(user.email, token)
    # ElasticSearch
    try:
        doc = {
            "username": user.username,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "achievements": [],
        }
        await es.index(index="users", id=user.id, body=doc)
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": f"Ошибка в апдейте elastic search: {e}"},
        )
    # Redis
    cache_info = {"posts_count": 0, "followers_count": 0, "following_count": 0}
    await redis_cache.hset(f"user:{user.id}", cache_info)


async def on_after_forgot_password(user: schemas.UserDB, token: str, request: Request):
    print(f"User {user.id} has forgot their password. Reset token: {token}")


async def on_after_update(
    user: schemas.UserDB, update_dict: Dict[str, Any], request: Request
):
    try:
        doc_updated = {
            {
                "doc": {
                    "username": user.username,
                    "email": user.email,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                }
            }
        }
        await es.update(index="users", id=user.id, body=doc_updated)
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": f"Ошибка в апдейте elastic search: {e}"},
        )


def setup_users(app):

    app.include_router(
        get_auth_router(jwt_authentication, user_db, fastapi_users.authenticator),
        prefix="/core/auth",
        tags=["Auth"],
    )
    app.include_router(
        get_register_router(
            fastapi_users.create_user,
            schemas.User,
            schemas.UserCreate,
            user_db,
            fastapi_users.authenticator,
            after_register=on_after_register,
            validate_password=validate_password,
        ),
        prefix="/core/auth",
        tags=[],
    )
    app.include_router(
        fastapi_users.get_reset_password_router(
            SECRET, after_forgot_password=on_after_forgot_password
        ),
        prefix="/core/auth",
        tags=["Auth"],
    )
    app.include_router(
        get_verify_router(
            fastapi_users.verify_user, fastapi_users.get_user, schemas.User, SECRET
        ),
        prefix="/core/auth",
        tags=["Auth"],
    )
    app.include_router(
        get_users_router(
            user_db,
            schemas.User,
            schemas.UserUpdate,
            schemas.UserDB,
            fastapi_users.authenticator,
            validate_password=validate_password,
            after_update=on_after_update,
        ),
        prefix="/core/profile",
        tags=["Profile"],
    )

    @app.on_event("startup")
    async def startup():
        await database.connect()

    @app.on_event("shutdown")
    async def shutdown():
        await database.disconnect()
