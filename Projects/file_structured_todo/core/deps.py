from typing_extensions import Annotated
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

from .db.session import sessionLocal

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with sessionLocal() as db:
        try:
            yield db
            await db.commit()
        except Exception as e:
            await db.rollback()
            raise
        finally:
            await db.close()


SessionDep = Annotated[AsyncSession, Depends(get_db)]
