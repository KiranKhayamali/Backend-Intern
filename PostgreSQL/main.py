from typing import Annotated
from fastapi import FastAPI, Depends, Query, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager
from models import User, Base, UserSchema, UserUpdate
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

@app.get("/users/{user_id}", response_model=UserSchema)
async def read_user(user_id: int, db: SessionDep):
    user = await db.get(User, user_id)
    return user

@app.post("/users/", response_model=UserSchema)
async def create_user(name:str, email:str, db: SessionDep):
    user= User(name=name, email=email)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user

@app.patch("/users/{user_id}", response_model=UserSchema)
async def update_user(user_id: int, user: UserUpdate, db:SessionDep):
    user_db = await db.get(User, user_id)
    if not user_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User Not Found!")
    user_data = user.model_dump(exclude_unset=True)
    for key, value in user_data.items():
        setattr(user_db, key, value)

    await db.commit()
    await db.refresh(user_db)
    return user_db

@app.delete("/users/{user_id}")
async def delete_user(user_id: int, db:SessionDep):
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User Not Found!")
    await db.delete(user)
    await db.commit()
    return{"message": f"{user.name} has been successfully deleted from the database."}