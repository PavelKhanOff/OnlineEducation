from sqlalchemy import Column, Integer, String

from app.database import Base


class Tag(Base):
    __tablename__ = 'Tags'
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(50), nullable=False, unique=True)
