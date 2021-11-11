from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_pagination import add_pagination

from app.achievements import achievements
from app.auth.auth import setup_users
from app.categories import categories
from app.courses import courses
from app.database import Base, engine
from app.email import email
from app.file import file
from app.follows import follows
from app.homework import homework
from app.lessons import lessons
from app.content import contents
from app.middleware import middleware
from app.additional_functions import additional_function
from app.tags import tags
from app.users import users


from redis_conf.redis import redis_cache


app = FastAPI(
    openapi_url="/core/openapi.json", docs_url="/core/docs", redoc_url="/core/redoc"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


setup_users(app)

app.include_router(users.router)
app.include_router(achievements.router)
app.include_router(follows.router)
app.include_router(categories.router)
app.include_router(courses.router)
app.include_router(lessons.router)
app.include_router(contents.router)
app.include_router(tags.router)
app.include_router(homework.router)
app.include_router(file.router)
app.include_router(middleware.router)
app.include_router(email.router)
app.include_router(additional_function.router)

add_pagination(app)


@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await redis_cache.init_cache()


@app.on_event("shutdown")
async def shutdown():
    await redis_cache.wait_closed()
