from fastapi_users.db.sqlalchemy import GUID
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    Table,
)
from sqlalchemy.orm import relationship, backref
from sqlalchemy.sql import func
from app.database import Base


course_tags_association = Table(
    'course-tags',
    Base.metadata,
    Column('Course_id', Integer, ForeignKey('Courses.id')),
    Column('Tag_id', Integer, ForeignKey('Tags.id')),
)


class Course(Base):
    __tablename__ = 'Courses'
    id = Column(Integer, primary_key=True, index=True)
    cover = relationship(
        "Avatar",
        lazy='joined',
        uselist=False,
        backref=backref("cover_course", uselist=False),
    )
    title = Column(String(50), nullable=False)
    price = Column(Integer, nullable=False, default=0)
    description = Column(Text)
    created_at = Column(
        DateTime(timezone=True), nullable=True, server_default=func.now()
    )
    is_active = Column(Boolean)
    is_deleted = Column(Boolean, default=False)
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    user_id = Column(GUID, ForeignKey("Users.id"))
    user = relationship("User", back_populates="courses")
    category = Column(Integer, ForeignKey("Categories.id"))
    lessons = relationship('Lesson', lazy="select", backref='course')
    files = relationship('File', lazy="select", backref='course')
    is_visible = Column(Boolean, default=True)
    tags = relationship(
        'Tag', secondary=course_tags_association, backref='courses', lazy='select'
    )
