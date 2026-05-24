from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import  declarative_base

from ..config import settings

async_engine = create_async_engine(settings.DATABASE_URL)


Base = declarative_base()
