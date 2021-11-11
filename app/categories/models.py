from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database import Base


class Category(Base):
    __tablename__ = 'Categories'
    id = Column(Integer, primary_key=True, index=True)
    image = Column(String(255), nullable=False, default='image_default.png')
    title = Column(String(50), nullable=False)
    description = Column(Text)
    courses = relationship('Course', backref='category_obj')
