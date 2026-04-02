from sqlalchemy import Column, Integer, String
from database import Base
from pydantic import BaseModel

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True, nullable=False)

class UserSchema(BaseModel):
    id: int | None = None
    name: str
    email: str 

    class Config:
        orm_mode = True

class UserUpdate(BaseModel):
    id: int | None = None 
    name: str | None = None 
    email: str | None = None