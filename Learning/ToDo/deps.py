from typing_extensions import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

from .database import sessionLocal

async def get_db():
    db = sessionLocal()
    try:
        yield db 
    finally:
        await db.close()

SessionDep = Annotated[AsyncSession, Depends(get_db)]
