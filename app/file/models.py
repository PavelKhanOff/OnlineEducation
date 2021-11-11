from fastapi_users.db.sqlalchemy import GUID
from sqlalchemy import Column, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from app.database import Base


class File(Base):
    __tablename__ = 'Files'
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(50), nullable=False)
    description = Column(Text)
    url = Column(String(500), nullable=True, default='file_default.png')
    duration = Column(Integer, nullable=True)
    type = Column(String(50))
    homework_id = Column(Integer, ForeignKey("Homework.id"))
    course_id = Column(Integer, ForeignKey("Courses.id"))
    user = Column(GUID, ForeignKey("Users.id"))
    achievement_id = Column(Integer, ForeignKey("Achievements.id"))
    key = Column(String(255), nullable=False)
    content_id = Column(Integer, ForeignKey("Contents.id"))


class Avatar(Base):
    __tablename__ = 'Avatars'
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(50), nullable=False)
    url = Column(String(500), nullable=True, default='file_default.png')
    course_id = Column(Integer, ForeignKey("Courses.id"))
    user_id = Column(GUID, ForeignKey("Users.id"))
    achievement_id = Column(Integer, ForeignKey("Achievements.id"))
    key = Column(String(500), nullable=False)
