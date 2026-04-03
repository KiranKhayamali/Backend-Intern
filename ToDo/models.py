from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base 
from pydantic import BaseModel
from typing import List

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String)
    password = Column(String)

    notes = relationship("Note", back_populates="owner")
    
class Note(Base):
    __tablename__ = "todo_lists"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, unique=True, index=True)
    memo = Column(String)

    user_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="notes")

class NoteSchema(BaseModel):
    id: int | None = None
    title: str
    memo: str 

    model_config = {
        "from_attributes": True  
    }

class UserCreate(BaseModel):
    username: str 
    password: str 

class UserSchema(UserCreate):
    id: int | None = None
    username: str 
    notes: List[NoteSchema] = []

    model_config = {
        "from_attributes": True
    }
