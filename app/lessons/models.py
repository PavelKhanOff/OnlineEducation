from sqlalchemy import Column, ForeignKey, Integer, String, Table, Text
from sqlalchemy.orm import relationship

from app.database import Base

lessons_tags_association = Table(
    'lessons-tags',
    Base.metadata,
    Column('Lesson_id', Integer, ForeignKey('Lessons.id')),
    Column('Tag_id', Integer, ForeignKey('Tags.id')),
)


class Lesson(Base):
    __tablename__ = 'Lessons'
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(50), nullable=False)
    description = Column(Text)
    contents = relationship('Content', backref='lesson')
    rating = Column(Integer, nullable=True)
    estimated_time = Column(String(50), nullable=False)
    course_id = Column(Integer, ForeignKey("Courses.id"))
    homework = relationship('Homework', backref='lesson')
    tags = relationship(
        'Tag', secondary=lessons_tags_association, backref='lessons', lazy='joined'
    )
