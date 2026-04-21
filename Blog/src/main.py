from contextlib import asynccontextmanager
from datetime import UTC, datetime

from fastapi import FastAPI

from .app.core import logger as _logger_config
from .app.core.schemas import HealthCheck
from .app.core.db.session import async_engine
from .app.models.base import Base
from .app.api import users, posts, login, logout, comments
from .app.middlewares.logger_middleware import LoggerMiddleware


@asynccontextmanager
async def database_lifespan(app: FastAPI):
    print("App is Starting...........")
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    print("App is Shutting Down........")


# NOTE: Currently unused. If importing this file should trigger logger setup side effects,
# keep this import; otherwise it can be safely removed.
_ = _logger_config

# NOTE: Currently unused because middleware registration is commented out below.
_ = LoggerMiddleware

app = FastAPI(lifespan=database_lifespan)


@app.get("/", response_model=HealthCheck)
def root():
    return HealthCheck(
        status="OK",
        environment="Development",
        version="1.0.0",
        timestamp=datetime.now(UTC).isoformat(),
    )


app.add_middleware(LoggerMiddleware)

app.include_router(users.router)
app.include_router(posts.router)
app.include_router(login.router)
app.include_router(logout.router)
app.include_router(comments.router)
