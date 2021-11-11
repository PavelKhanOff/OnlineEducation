from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from fastapi_pagination.ext.async_sqlalchemy import paginate
from . import schemas
from app.pagination import CustomPage as Page
from app.email.em_dal import EmailDAL
from app.email.dependencies import get_email_dal


router = APIRouter(tags=['Email'])


@router.post(
    '/core/email', response_model=Page[schemas.PreRegisterSchema], status_code=200
)
async def pre_registration_email(
    request: schemas.PreRegisterSchema, email_dal: EmailDAL = Depends(get_email_dal)
):
    if await email_dal.get_pre_user_by_email(request.email):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": "Вы уже зарегистрированы"},
        )
    await email_dal.create_pre_user(request)
    return JSONResponse(status_code=status.HTTP_200_OK, content={"message": "Success"})


@router.get(
    '/core/email', response_model=Page[schemas.PreRegisterSchema], status_code=200
)
async def get_pre_registration_email(email_dal: EmailDAL = Depends(get_email_dal)):
    pre_users = await email_dal.get_pre_users_query()
    return await paginate(email_dal.db_session, pre_users)
