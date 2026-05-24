from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from ..core.db.database import Base


class Note(Base):
    __tablename__ = "todo_lists"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, unique=True, index=True)
    memo = Column(String)

    user_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="notes")
