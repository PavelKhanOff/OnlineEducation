from app.achievements.models import Achievement
from app.config import MIDDLEWARE_URL_SEND_NOTIFICATIONS
import httpx
from app.database import async_session
from app.middleware.middleware_dal import MiddlewareDAL


async def add_achievements(author_id, follow_dal):
    author = await follow_dal.get_user_with_followers(author_id)
    if len(author.followers) >= 1000:
        achievement = await follow_dal.get_achievement('1000 подписчиков')
        author.achievements.append(achievement)
        await follow_dal.db_session.flush()
    if len(author.followers) >= 10000:
        achievement = await follow_dal.get_achievement('10000 подписчиков')
        author.achievements.append(achievement)
        await follow_dal.db_session.flush()
    if len(author.followers) >= 100000:
        achievement = await follow_dal.get_achievement('100000 подписчиков')
        author.achievements.append(achievement)
        await follow_dal.db_session.flush()


async def send_follow_notifications(user_id, author):
    url = MIDDLEWARE_URL_SEND_NOTIFICATIONS
    async with async_session() as session:
        async with session.begin():
            dal = MiddlewareDAL(session)
            user = str(await dal.get_user_username(user_id))
            token = await dal.get_superuser_token()
    headers = {'Authorization': f'Bearer {token}'}
    data = {
        'notification_type': 'Подписка',
        'title': 'Подписка',
        'text': f'{user} подписался на Вас',
        'user_id': str(user_id),
        'receivers': [str(author)]
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
