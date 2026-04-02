from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

from dotenv import load_dotenv
import os 

load_dotenv()

DB_URL = os.getenv("DATABASE_URL")

# #Normal Database connection
# engine = create_engine(DATABASE_URL)
# sessionLocal = sessionmaker(
#     autocommit=False,
#     autoflush=False,
#     bind=engine
# )

#Async Version for better performance
if not isinstance(DB_URL, str):
    raise ValueError(f"DATABASE_URL must be a string, got {DB_URL}")
engine = create_async_engine(DB_URL) # Engine are the connection to the Database
sessionLocal = sessionmaker( #Session are used to communicate with the Database
    engine, class_=AsyncSession, expire_on_commit=False
)

Base = declarative_base()