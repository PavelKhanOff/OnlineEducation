from fastapi_users.db.sqlalchemy import GUID
from sqlalchemy import Column, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from app.database import Base


class Content(Base):
    __tablename__ = 'Contents'
    id = Column(Integer, primary_key=True, index=True)
    text = Column(String(500), nullable=True)
    lesson_id = Column(Integer, ForeignKey("Lessons.id"))
    files = relationship('File', lazy='joined', backref='content')
