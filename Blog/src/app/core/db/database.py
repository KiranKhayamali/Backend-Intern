from sqlalchemy.ext.asyncio import create_async_engine
from ..config import settings
from ...models.base import Base


DATABASE_URI = settings.POSTGRES_URI
DATABASE_PREFIX = settings.POSTGRES_ASYNC_PREFIX
DATABASE_URL = f"{DATABASE_PREFIX}{DATABASE_URI}"


async_engine = create_async_engine(DATABASE_URL, echo=False, future=True)

async def init_db() -> None:
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_db() -> None:
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)