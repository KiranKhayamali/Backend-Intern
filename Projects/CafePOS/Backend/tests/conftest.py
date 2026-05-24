import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from typing import AsyncGenerator

from Projects.CafePOS.Backend.src.main import app
from Projects.CafePOS.Backend.src.app.models.base import Base
from Projects.CafePOS.Backend.src.app.core.db.session import get_db


TEST_DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/test_db"

engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestingSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
    async with TestingSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            raise e
        finally:
            await session.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
async def setup_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.fixture
async def client():
    import httpx

    transport = httpx.ASGITransport(app=app)

    async with httpx.AsyncClient(
        transport=transport,
        base_url="http://testserver"
    ) as ac:
        yield ac

