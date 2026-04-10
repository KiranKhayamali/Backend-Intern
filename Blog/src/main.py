from fastapi import FastAPI
from contextlib import asynccontextmanager
from .app.core.db.session import async_engine
from .app.models.base import Base
from .app.api import users, posts, login
from .app.core.schemas import HealthCheck
from datetime import UTC, datetime


@asynccontextmanager
async def database_lifespan(app: FastAPI):
    print("App is Starting...........")
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    print("App is Shutting Down........")

app = FastAPI(lifespan=database_lifespan)


@app.get("/", response_model=HealthCheck)
def root():
    return HealthCheck(
        status="OK",
        environment="Development",
        version="1.0.0",
        timestamp=datetime.now(UTC).isoformat()
    )


app.include_router(users.router)
app.include_router(posts.router)
app.include_router(login.router)