import os 
from enum import Enum

from pydantic import SecretStr, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    APP_NAME: str = os.getenv("APP_NAME")
    APP_DESCRIPTION: str | None = os.getenv("APP_DESCRIPTION")
    APP_VERSION: str | None = os.getenv("APP_VERSION")
    LICENSE_NAME: str | None = os.getenv("LICENSE_NAME")
    CONTACT_NAME: str | None = os.getenv("CONTACT_NAME")    
    CONTACT_EMAIL: str | None = os.getenv("CONTACT_EMAIL")


class CryptSetting(BaseSettings):
    SECRET_KEY: SecretStr = os.getenv("SECRET_KEY")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60))
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", 7))


class DatabaseSettings(BaseSettings):
    pass


class PostgresSettings(DatabaseSettings):
    POSTGRES_USER: str = os.getenv("POSTGRES_USER") 
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD")
    POSTGRES_SERVER: str = os.getenv("POSTGRES_SERVER", "localhost")
    POSTGRES_PORT: int = int(os.getenv("POSTGRES_PORT", 5432))
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "blog")
    POSTGRES_ASYNC_PREFIX: str = os.getenv("POSTGRES_ASYNC_PREFIX", "postgresql+asyncpg://")
    POSTGRES_URL: str | None = None

    @computed_field  # type: ignore[prop-decorator]
    @property
    def POSTGRES_URI(self) -> str:
        credentials = f"{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
        location = f"{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        return f"{credentials}@{location}"
    

class FileLoggerSettings(DatabaseSettings):
    FILE_LOG_MAX_BYTES: int = 10 * 1024 * 1024 
    FILE_LOG_BACKUP_COUNT: int = 5 
    FILE_LOG_FORMAT_JSON: bool = True 
    FILE_LOG_LEVEL: str = "INFO"

    FILE_LOG_INCLUDE_REQUEST_ID: bool = True 
    FILE_LOG_INCLUDE_PATH: bool = True 
    FILE_LOG_INCLUDE_METHOD: bool = True 
    FILE_LOG_INCLUDE_CLIENT_HOST: bool = True 
    FILE_LOG_INCLUDE_STATUS_CODE: bool = True 


class RedisSettings(DatabaseSettings):
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", 6379))


class Settings(AppSettings, CryptSetting, PostgresSettings,FileLoggerSettings, RedisSettings):
    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "..", ".env"),
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

settings = Settings()
