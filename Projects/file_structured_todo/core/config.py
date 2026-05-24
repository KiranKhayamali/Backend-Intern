from dotenv import load_dotenv
from pathlib import Path
import os

# Load .env from the project root (two levels up from this file)
base_dir = Path(__file__).resolve().parent.parent
env_path = base_dir / '.env'
load_dotenv(dotenv_path=env_path)


class Settings:
    DATABASE_URL: str = os.getenv("TODO_DATABASE_URL")
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))


settings = Settings()