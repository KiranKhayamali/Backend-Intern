import pytest
from sqlalchemy import text
from unittest.mock import AsyncMock, Mock, patch

from Projects.CafePOS.Backend.src.app.core.db.session import get_db
from Projects.CafePOS.Backend.src.app.core.db.database import init_db, drop_db
from Projects.CafePOS.Backend.src.app.models.base import Base


@pytest.mark.asyncio
async def test_get_db_commit_success():
    fake_session = AsyncMock()
    mock_context_manager = AsyncMock()
    mock_context_manager.__aenter__.return_value = fake_session
    mock_context_manager.__aexit__.return_value = None

    with patch(
        "src.app.core.db.session.async_session",
        return_value=mock_context_manager
    ):
        generator = get_db() #Create generator
        db = await anext(generator) #Enter the generator(yield db)
        assert db == fake_session
        with pytest.raises(StopAsyncIteration):
            await anext(generator) #Exit the generator, should raise StopAsyncIteration

        fake_session.commit.assert_awaited_once()
        fake_session.rollback.assert_not_awaited()
        fake_session.close.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_db_rollback_on_exception():
    fake_session = AsyncMock()
    mock_context_manager = AsyncMock()
    mock_context_manager.__aenter__.return_value = fake_session
    mock_context_manager.__aexit__.return_value = None

    with patch(
        "src.app.core.db.session.async_session",
        return_value=mock_context_manager
    ):
        generator = get_db() #Create generator
        await anext(generator) #Enter the generator(yield db)
        with pytest.raises(ValueError):
            await generator.athrow(ValueError("Database Error")) #Exit the generator with exception

        fake_session.commit.assert_not_awaited()
        fake_session.rollback.assert_awaited_once()
        fake_session.close.assert_awaited_once()



@pytest.mark.asyncio
async def test_init_db_calls_create_all():
    mock_conn = AsyncMock()
    mock_context_manager = AsyncMock()
    mock_context_manager.__aenter__.return_value = mock_conn
    mock_context_manager.__aexit__.return_value = None
    mock_engine = AsyncMock()
    mock_engine.begin = Mock(return_value=mock_context_manager)

    with patch(
        "src.app.core.db.database.async_engine",
        new=mock_engine
    ):
        await init_db()
        mock_conn.run_sync.assert_awaited_once_with(Base.metadata.create_all)


@pytest.mark.asyncio
async def test_drop_db_calls_drop_all():
    mock_conn = AsyncMock()
    mock_context_manager = AsyncMock()
    mock_context_manager.__aenter__.return_value = mock_conn
    mock_context_manager.__aexit__.return_value = None
    mock_engine = AsyncMock()
    mock_engine.begin = Mock(return_value=mock_context_manager)

    with patch(
        "src.app.core.db.database.async_engine",
        new=mock_engine
    ):
        await drop_db()
        mock_conn.run_sync.assert_awaited_once_with(Base.metadata.drop_all)
