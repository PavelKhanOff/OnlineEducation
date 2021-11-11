from sqlalchemy import Column, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database import Base


class Homework(Base):
    __tablename__ = 'Homework'
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(50), nullable=False)
    description = Column(Text)
    lesson_id = Column(Integer, ForeignKey("Lessons.id"))
    files = relationship('File', backref='homework')
