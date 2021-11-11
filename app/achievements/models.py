from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import backref, relationship
from app.database import Base


class Achievement(Base):
    __tablename__ = 'Achievements'
    id = Column(Integer, primary_key=True, index=True)
    avatar = relationship(
        "Avatar",
        lazy='joined',
        uselist=False,
        backref=backref("cover_achievement", uselist=False),
    )
    title = Column(String(50), unique=True, nullable=False)
    description = Column(Text)
