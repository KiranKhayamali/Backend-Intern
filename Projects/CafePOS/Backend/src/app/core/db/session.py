from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from typing import AsyncGenerator, Annotated
from fastapi import Depends

from .database import async_engine

async_session = async_sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as db:
        try:
            yield db
            await db.commit()
        except Exception as e:
            await db.rollback()
            raise
        finally:
            await db.close()

SessionDep = Annotated[AsyncSession, Depends(get_db)]