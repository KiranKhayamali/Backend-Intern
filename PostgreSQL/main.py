from typing import Annotated
from fastapi import FastAPI, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager
from models import User, Base, UserSchema
from database import engine
from deps import get_db

SessionDep = Annotated[AsyncSession, Depends(get_db)]

@asynccontextmanager
async def database_lifespan(app: FastAPI):
    print("App is Starting.....")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield 
    
    print("App is Shutting Down.....")

app = FastAPI(lifespan=database_lifespan) 

@app.get("/users/", response_model=list[UserSchema])
async def read_users(db: SessionDep, offset:int = 0, limit: Annotated[int, Query(le=10)] = 10):
    select_sql = select(User).offset(offset).limit(limit)
    result = await db.execute(select_sql)
    users = result.scalars().all()
    return users 




@app.post("/users/", response_model=UserSchema)
async def create_user(name:str, email:str, db: SessionDep):
    user= User(name=name, email=email)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user
