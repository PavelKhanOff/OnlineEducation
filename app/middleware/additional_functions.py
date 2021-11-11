from app.config import MIDDLEWARE_URL_SEND_NOTIFICATIONS
import httpx
from app.database import async_session
from app.middleware.middleware_dal import MiddlewareDAL


async def send_subscription_notifications(user_id, course):
    url = MIDDLEWARE_URL_SEND_NOTIFICATIONS
    async with async_session() as session:
        async with session.begin():
            dal = MiddlewareDAL(session)
            user = str(await dal.get_user_username(user_id))
            token = await dal.get_superuser_token()
    headers = {'Authorization': f'Bearer {token}'}
    data = {
        'notification_type': 'Subscription',
        'title': 'Подписка',
        'text': f'{user} подписался на ваш курс {course.title}',
        'user_id': str(user_id),
        'receivers': [str(course.user_id)]
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
