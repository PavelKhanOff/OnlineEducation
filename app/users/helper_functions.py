from app.config import MIDDLEWARE_URL_GET_POSTS_COUNT
import requests

# def get_posts_count():
#     url = f'{MIDDLEWARE_URL_GET_POSTS_COUNT}'
#     try:
#         response = requests.get(url=url, timeout=8)
#     except requests.exceptions.ConnectionError as e:
#         return {'Ошибка': e}
#     except Exception as e:
#         return {'Ошибка': e}
#     return response.json()
#
#
# user_posts_count = {}
