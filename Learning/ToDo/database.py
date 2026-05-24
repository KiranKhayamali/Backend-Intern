from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

from dotenv import load_dotenv
import os

load_dotenv()

def _read_secret_file(path: str | None) -> str | None:
    if not path:
        return None
    try:
        with open(path, "r", encoding="utf-8") as secret_file:
            value = secret_file.read().strip()
            return value or None
    except OSError:
        return None


DATABASE_URL = (
    os.getenv("TODO_DATABASE_URL")
    or os.getenv("DATABASE_URL")
    or _read_secret_file(os.getenv("TODO_DATABASE_URL_FILE"))
    or _read_secret_file(os.getenv("DATABASE_URL_FILE"))
)

if not isinstance(DATABASE_URL, str):
    raise ValueError(
        "Missing database URL. Set TODO_DATABASE_URL/DATABASE_URL or use TODO_DATABASE_URL_FILE/DATABASE_URL_FILE."
    )

engine = create_async_engine(DATABASE_URL)
sessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

Base = declarative_base()