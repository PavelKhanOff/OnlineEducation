from fastapi_users import InvalidPasswordException
from typing import Union
from app.config import FEED_URL_GET_POST, FEED_URL_CHECK_POST
import requests
from app.users.schemas import User, UserCreate
import httpx


async def validate_password(password: str, user: Union[UserCreate, User]):
    if len(password) < 8:
        raise InvalidPasswordException(
            reason="Password should be at least 8 characters"
        )
    if user.email in password:
        raise InvalidPasswordException(reason="Password should not contain e-mail")


def get_post(post_id: int):
    url = f'{FEED_URL_GET_POST}{post_id}'
    try:
        response = requests.get(url=url, timeout=8)
    except requests.exceptions.ConnectionError as e:
        return {'Ошибка': e}
    except Exception as e:
        return {'Ошибка': e}
    return response.json()


async def check_post(post_id):
    url = f'{FEED_URL_CHECK_POST}{post_id}'
    async with httpx.AsyncClient() as client:
        response = await client.get(url=url, timeout=8)
        response.raise_for_status()
    return response.json()
