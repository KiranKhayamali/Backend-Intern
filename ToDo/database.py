from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("TODO_DATABASE_URL")

if not isinstance(DATABASE_URL, str):
    raise ValueError(f"DATABASE_URL must be a string, got {DATABASE_URL}")

engine = create_async_engine(DATABASE_URL)
sessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

Base = declarative_base()