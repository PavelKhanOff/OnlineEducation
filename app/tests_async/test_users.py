import pytest
from httpx import AsyncClient
from main import app
import logging
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.exc import SQLAlchemyError
from typing import AsyncIterator
from app.database import get_db

logger = logging.getLogger(__name__)


SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True,
    pool_size=20,
    max_overflow=10
)

async_session = sessionmaker(
    bind=engine, autoflush=False, future=True, class_=AsyncSession
)
Base = declarative_base()


Base.metadata.create_all(bind=engine)


async def override_get_db() -> AsyncIterator[sessionmaker]:
    try:
        yield async_session
    except SQLAlchemyError as e:
        logger.exception(e)


app.dependency_overrides[get_db] = override_get_db


@pytest.mark.asyncio
async def test_root():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/core/users")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_root2():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/core/achievements")
    assert response.status_code == 200
