from sqlalchemy import Column, Integer, String

from app.database import Base


class PreRegister(Base):
    __tablename__ = "Preregister"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(50), nullable=False)
