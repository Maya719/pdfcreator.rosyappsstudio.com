from sqlalchemy import Column, Integer, String
from database.connection.db import Base
from app.models.Base import BaseModel


class User(Base, BaseModel):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(255))
    password = Column(String(255))
