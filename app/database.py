from sqlalchemy.orm import declarative_base
import logging
from app.config import SQLALCHEMY_DATABASE_URL
from typing import AsyncIterator


from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

logger = logging.getLogger(__name__)

engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True,
    pool_size=20,
    max_overflow=10,
    echo=True,
)

async_session = sessionmaker(
    bind=engine, autoflush=False, future=True, class_=AsyncSession
)
Base = declarative_base()


async def get_db() -> AsyncIterator[sessionmaker]:
    try:
        yield async_session
    except SQLAlchemyError as e:
        logger.exception(e)


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
