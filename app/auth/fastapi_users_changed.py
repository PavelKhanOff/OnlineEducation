import jwt
from fastapi_users.user import (
    GetUserProtocol,
    UserAlreadyVerified,
    UserNotExists,
    VerifyUserProtocol,
)
from fastapi_users.utils import JWT_ALGORITHM, generate_jwt
from typing import Any, Callable, Dict, Optional, Type, cast
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status, Body
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_users import models
from fastapi_users.authentication import Authenticator, BaseAuthentication
from fastapi_users.db import (
    BaseUserDatabase,
    SQLAlchemyUserDatabase,
)
from fastapi_users.password import get_password_hash
from fastapi_users.router.common import ErrorCode, run_handler
from fastapi_users.user import (
    CreateUserProtocol,
    InvalidPasswordException,
    UserAlreadyExists,
    ValidatePasswordProtocol,
)
from pydantic import UUID4, EmailStr
from sqlalchemy import func, or_

from app.schemas import Token, UserLogin
from app.users.user_dal import UserDAL
from app.users.dependencies import get_user_dal
from app.users.schemas import UserOut


class OverridenSQLAlchemyUserDatabase(SQLAlchemyUserDatabase):
    async def get_by_email(self, username_or_mail: str):
        query = self.users.select().where(
            or_(
                func.lower(self.users.c.username) == func.lower(username_or_mail),
                func.lower(self.users.c.email) == func.lower(username_or_mail),
            )
        )
        user = await self.database.fetch_one(query)
        return await self._make_user(user) if user else None


def get_auth_router(
    backend: BaseAuthentication,
    user_db: BaseUserDatabase[models.BaseUserDB],
    authenticator: Authenticator,
    requires_verification: bool = False,
) -> APIRouter:
    """Generate a router with login/logout routes for an authentication backend."""
    router = APIRouter()
    get_current_user = authenticator.current_user(
        active=True, verified=requires_verification
    )

    @router.post("/login", response_model=Token)
    async def login(
        # Ask for the two fields in the request
        response: Response,
        request: UserLogin,
    ):
        # Manually instantiate an `OAuth2PasswordRequestForm` with their values
        credentials = OAuth2PasswordRequestForm(
            username=request.username, password=request.password, scope=""
        )
        user = await user_db.authenticate(credentials)

        if user is None or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ErrorCode.LOGIN_BAD_CREDENTIALS,
            )
        if requires_verification and not user.is_verified:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ErrorCode.LOGIN_USER_NOT_VERIFIED,
            )
        return await backend.get_login_response(user, response)

    if backend.logout:

        @router.post("/logout")
        async def logout(response: Response, user=Depends(get_current_user)):
            return await backend.get_logout_response(user, response)

    return router


def get_register_router(
    create_user: CreateUserProtocol,
    user_model: Type[models.BaseUser],
    user_create_model: Type[models.BaseUserCreate],
    user_db: BaseUserDatabase[models.BaseUserDB],
    authenticator: Authenticator,
    after_register: Optional[Callable[[models.UD, Request], None]] = None,
    validate_password: Optional[ValidatePasswordProtocol] = None,
) -> APIRouter:
    """Generate a router with the register route."""
    router = APIRouter()
    get_current_superuser = authenticator.current_user(active=True, superuser=True)

    @router.get(
        "/authenticate",
        tags=["Superuser"],
        include_in_schema=False,
        status_code=status.HTTP_200_OK,
        dependencies=[Depends(get_current_superuser)],
    )
    async def authenticate(request: Request):
        return Response(status_code=200)

    @router.post(
        "/register",
        tags=["Auth"],
        response_model=user_model,
        status_code=status.HTTP_201_CREATED,
    )
    async def register(request: Request, user: user_create_model):  # type: ignore
        user = cast(user_create_model, user)  # Prevent mypy complain
        db_user = await user_db.get_by_email(user.username)
        if db_user is not None:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                detail=ErrorCode.REGISTER_USER_ALREADY_EXISTS,
            )
        if validate_password:
            try:
                await validate_password(user.password, user)
            except InvalidPasswordException as e:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={
                        "code": ErrorCode.REGISTER_INVALID_PASSWORD,
                        "reason": e.reason,
                    },
                )
        try:
            created_user = await create_user(user, safe=True)
        except UserAlreadyExists:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ErrorCode.REGISTER_USER_ALREADY_EXISTS,
            )
        if after_register:
            await run_handler(after_register, created_user, request)

        return created_user

    return router


def get_users_router(
    user_db: BaseUserDatabase[models.BaseUserDB],
    user_model: Type[models.BaseUser],
    user_update_model: Type[models.BaseUserUpdate],
    user_db_model: Type[models.BaseUserDB],
    authenticator: Authenticator,
    after_update: Optional[Callable[[models.UD, Dict[str, Any], Request], None]] = None,
    requires_verification: bool = False,
    validate_password: Optional[ValidatePasswordProtocol] = None,
) -> APIRouter:
    """Generate a router with the authentication routes."""
    router = APIRouter()

    get_current_active_user = authenticator.current_user(
        active=True, verified=requires_verification
    )
    get_current_superuser = authenticator.current_user(
        active=True, verified=requires_verification, superuser=True
    )

    async def _get_or_404(id: UUID4) -> models.BaseUserDB:
        user = await user_db.get(id)
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        return user

    async def _check_unique_email(
        updated_user: user_update_model,  # type: ignore
    ) -> None:
        updated_user = cast(
            models.BaseUserUpdate, updated_user
        )  # Prevent mypy complain
        if updated_user.email:
            user = await user_db.get_by_email(updated_user.email)
            if user is not None:
                raise HTTPException(
                    status.HTTP_400_BAD_REQUEST,
                    detail=ErrorCode.UPDATE_USER_EMAIL_ALREADY_EXISTS,
                )
        if updated_user.username:
            user = await user_db.get_by_email(updated_user.username)
            if user is not None:
                raise HTTPException(
                    status.HTTP_400_BAD_REQUEST,
                    detail=ErrorCode.UPDATE_USER_EMAIL_ALREADY_EXISTS,
                )

    async def _update_user(
        user: models.BaseUserDB, update_dict: Dict[str, Any], request: Request
    ):
        for field in update_dict:
            if field == "password":
                password = update_dict[field]
                if validate_password:
                    await validate_password(password, user)
                hashed_password = get_password_hash(password)
                user.hashed_password = hashed_password
            else:
                setattr(user, field, update_dict[field])
        updated_user = await user_db.update(user)
        if after_update:
            await run_handler(after_update, updated_user, update_dict, request)
        return updated_user

    @router.get("", response_model=UserOut)
    async def me(
        user_dal: UserDAL = Depends(get_user_dal),
        user: models.BaseUserDB = Depends(get_current_active_user),
    ):
        user = await user_dal.get_user(user_id=user.id)
        return user

    @router.patch(
        "",
        response_model=UserOut,
        dependencies=[Depends(get_current_active_user), Depends(_check_unique_email)],
    )
    async def update_me(
        request: Request,
        updated_user: user_update_model,  # type: ignore
        user: user_db_model = Depends(get_current_active_user),  # type: ignore
    ):
        updated_user = cast(
            models.BaseUserUpdate,
            updated_user,
        )  # Prevent mypy complain
        updated_user_data = updated_user.create_update_dict()

        try:
            return await _update_user(user, updated_user_data, request)
        except InvalidPasswordException as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "code": ErrorCode.UPDATE_USER_INVALID_PASSWORD,
                    "reason": e.reason,
                },
            )

    return router


VERIFY_USER_TOKEN_AUDIENCE = "fastapi-users:verify"


def get_verify_router(
    verify_user: VerifyUserProtocol,
    get_user: GetUserProtocol,
    user_model: Type[models.BaseUser],
    verification_token_secret: str,
    after_verification: Optional[Callable[[models.UD, Request], None]] = None,
):
    router = APIRouter()

    @router.get("/verify", response_model=user_model)
    async def verify(request: Request, token: str = "token"):
        try:
            data = jwt.decode(
                token,
                verification_token_secret,
                audience=VERIFY_USER_TOKEN_AUDIENCE,
                algorithms=[JWT_ALGORITHM],
            )
        except jwt.exceptions.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ErrorCode.VERIFY_USER_TOKEN_EXPIRED,
            )
        except jwt.PyJWTError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ErrorCode.VERIFY_USER_BAD_TOKEN,
            )

        user_id = data.get("user_id")
        email = cast(EmailStr, data.get("email"))

        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ErrorCode.VERIFY_USER_BAD_TOKEN,
            )

        try:
            user_check = await get_user(email)
        except UserNotExists:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ErrorCode.VERIFY_USER_BAD_TOKEN,
            )

        try:
            user_uuid = UUID4(user_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ErrorCode.VERIFY_USER_BAD_TOKEN,
            )

        if user_check.id != user_uuid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ErrorCode.VERIFY_USER_BAD_TOKEN,
            )

        try:
            user = await verify_user(user_check)
        except UserAlreadyVerified:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ErrorCode.VERIFY_USER_ALREADY_VERIFIED,
            )

        if after_verification:
            await run_handler(after_verification, user, request)

        return user

    return router


async def get_verify_token(
    email: EmailStr, get_user: GetUserProtocol, verification_token_secret
):
    try:
        user = await get_user(email)
        if not user.is_verified and user.is_active:
            token_data = {
                "user_id": str(user.id),
                "email": email,
                "aud": VERIFY_USER_TOKEN_AUDIENCE,
            }
            token = generate_jwt(token_data, verification_token_secret, 3600)

    except UserNotExists:
        pass

    return token
