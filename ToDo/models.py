from sqlalchemy import Column, Integer, String
from database import Base 
from pydantic import BaseModel

class Note(Base):
    __tablename__ = "todo_lists"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, unique=True, index=True)
    memo = Column(String)

class NoteSchema(BaseModel):
    id: int | None = None
    title: str
    memo: str 

    class Config:
        orm_mode = True