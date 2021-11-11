import os

# JWT CONFIG
SECRET = os.environ.get('JWTSECRET', 'SOMESECRET')

# Protocol
PROTOCOL = os.environ.get('PROTOCOL', 'http')

# POSTGRES CONFIGURATION
DB_ENGINE = os.environ.get('DB_ENGINE', 'postgresql+asyncpg')
DB_ENGINE_USERS = os.environ.get('DB_ENGINE', 'postgresql')
POSTGRES_USER = os.environ.get('POSTGRES_USER', 'admin')
POSTGRES_PASSWORD = os.environ.get('POSTGRES_PASSWORD', 'LOYAg3Wv')
# POSTGRES_HOST = os.environ.get('POSTGRES_HOST', 'eduonedb')
POSTGRES_HOST = os.environ.get('POSTGRES_HOST', 'db')
POSTGRES_PORT = os.environ.get('POSTGRES_PORT', '5432')
POSTGRES_DB = os.environ.get('POSTGRES_DB', 'eduonepostgresdb')
SQLALCHEMY_DATABASE_URL = (
    f"{DB_ENGINE}://{POSTGRES_USER}:"
    f"{POSTGRES_PASSWORD}@{POSTGRES_HOST}:"
    f"{POSTGRES_PORT}/"
    f"{POSTGRES_DB}"
)

SQLALCHEMY_DATABASE_URL_USERS = (
    f"{DB_ENGINE_USERS}://{POSTGRES_USER}:"
    f"{POSTGRES_PASSWORD}@{POSTGRES_HOST}:"
    f"{POSTGRES_PORT}/"
    f"{POSTGRES_DB}"
)

# Middleware
MIDDLEWARE_HOST = os.environ.get("MIDDLEWARE_HOST", "middleware-service")
MIDDLEWARE_PORT = os.environ.get("MIDDLEWARE_PORT", 6000)
# URL_GET_POSTS = os.environ.get("URL_CHECK_USER", 'middleware/get_posts')
URL_GET_POSTS_COUNT = os.environ.get(
    "URL_CHECK_USER", 'middleware/get_users_post_count'
)
SEND_NOTIFICATIONS = os.environ.get("SEND_NOTIFICATIONS", 'middleware/send_notifications')
MIDDLEWARE_URL_SEND_NOTIFICATIONS = (
    f'{PROTOCOL}://{MIDDLEWARE_HOST}:{MIDDLEWARE_PORT}/{SEND_NOTIFICATIONS}'
)

# FEED
FEED_HOST = os.environ.get("FEED_HOST", "feed-service")
FEED_PORT = os.environ.get("FEED_PORT", 7000)
URL_CHECK_POST = os.environ.get("URL_CHECK_POST", 'feed/middleware/post/check/')
URL_GET_POST = os.environ.get("URL_GET_POST", 'feed/middleware/post/')
FEED_URL_CHECK_POST = f'{PROTOCOL}://{FEED_HOST}:{FEED_PORT}/{URL_CHECK_POST}'
FEED_URL_GET_POST = f'{PROTOCOL}://{FEED_HOST}:{FEED_PORT}/{URL_GET_POST}'
# MIDDLEWARE_URL_GET_POSTS = (
#     f'{PROTOCOL}://{MIDDLEWARE_HOST}:{MIDDLEWARE_PORT}/{URL_GET_POSTS}'
# )
MIDDLEWARE_URL_GET_POSTS_COUNT = (
    f'{PROTOCOL}://{MIDDLEWARE_HOST}:{MIDDLEWARE_PORT}/{URL_GET_POSTS_COUNT}'
)


# EMAIL
EMAIL_HOST = os.environ.get("EMAIL_HOST", "email-service")
EMAIL_PORT = os.environ.get("EMAIL_PORT", 9001)
URL_SEND_REGISTER_MAIL = os.environ.get("URL_SEND_REGISTER_MAIL", "email/send")

EMAIL_URL_SEND_REGISTER_MAIL = (
    f'{PROTOCOL}://{EMAIL_HOST}:{EMAIL_PORT}/{URL_SEND_REGISTER_MAIL}'
)

# ElasticSearch
ELASTIC_HOST = os.environ.get("ELASTIC_HOST", "elasticsearch")
ELASTIC_PORT = os.environ.get("ELASTIC_PORT", 9200)

# Auth verify
HOST = os.environ.get("HOST", "localhost")
PORT = os.environ.get("PORT", "8000")
VERIFY_URL = os.environ.get("VERIFY_URL", "/core/auth/verify")
VERIFICATION_URL = f'{PROTOCOL}://{HOST}:{PORT}/{VERIFY_URL}'


# Redis conf
REDIS_HOST = os.environ.get("REDIS_HOST", "redis")
REDIS_PORT = os.environ.get("REDIS_PORT", "6379")
REDIS_PASSWORD = os.environ.get("REDIS_PASSWORD", "localhost")
