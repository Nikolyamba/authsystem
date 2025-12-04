from sqlalchemy import Column, Integer, String, Boolean

from server.database.session import Base

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(20), nullable=False)
    surname = Column(String(20), nullable=False)
    patronymic = Column(String(20), nullable=True)
    email = Column(String(50), nullable=False, unique=True)
    password = Column(String(128), nullable=False)
    is_active = Column(Boolean, default=True)