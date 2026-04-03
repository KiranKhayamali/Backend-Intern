from typing import Annotated, List
from fastapi import Depends, Query, HTTPException, status, APIRouter
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from ..models import User, UserSchema
from ..deps import get_db

SessionDep = Annotated[AsyncSession, Depends(get_db)]

router = APIRouter()

@router.get("/", response_model=List[UserSchema])
async def read_users(db:SessionDep, offset:int = 0, limit: Annotated[int, Query(le=5)] = 5):
    select_sql = select(User).options(selectinload(User.notes)).offset(offset).limit(limit)
    result = await db.execute(select_sql)
    users = result.scalars().all()
    if not users:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User Not Found")
    return users

@router.post("/")
async def create_user(user:UserSchema, db:SessionDep):
    print(user.model_dump())
    db_user = User(**user.model_dump())
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user
