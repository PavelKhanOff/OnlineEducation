from app.config import MIDDLEWARE_URL_SEND_NOTIFICATIONS
import httpx
from app.database import async_session
from app.middleware.middleware_dal import MiddlewareDAL


async def send_course_notifications(user_id):
    url = MIDDLEWARE_URL_SEND_NOTIFICATIONS
    async with async_session() as session:
        async with session.begin():
            dal = MiddlewareDAL(session)
            user = str(await dal.get_user_username(user_id))
            followers = [str(user) for user in await dal.get_user_with_followers(user_id)]
            token = await dal.get_superuser_token()
    headers = {'Authorization': f'Bearer {token}'}
    data = {
        'notification_type': 'Course',
        'title': 'Новый курс',
        'text': f'Новый курс у {user}',
        'user_id': str(user_id),
        'receivers': followers
    }
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url=url, json=data, headers=headers, timeout=8)
            response.raise_for_status()
    except httpx.HTTPError as e:
        raise e
    except Exception as e:
        raise e
    return response.json()
