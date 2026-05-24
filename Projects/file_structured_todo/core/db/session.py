from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from .database import async_engine

sessionLocal = async_sessionmaker(
    bind=async_engine, class_=AsyncSession, expire_on_commit=False
)
