from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from typing import AsyncGenerator

from .database import async_engine


local_session = async_sessionmaker(bind=async_engine, class_=AsyncSession, expire_on_commit=False)


async def async_get_db() -> AsyncGenerator[AsyncSession, None]:
    async with local_session() as db:
        try:
            yield db
            await db.commit()
        except Exception as e:
            await db.rollback()
            raise 
        finally:
            await db.close()
