from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager
import models
from database import engine
from deps import get_db



@asynccontextmanager
async def database_lifespan(app: FastAPI):
    print("App is Starting.....")
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)

    yield 
    
    print("App is Shutting Down.....")

app = FastAPI(lifespan=database_lifespan) 


@app.post("/users/")
async def create_user(name:str, email:str, db: AsyncSession = Depends(get_db)):
    user= models.User(name=name, email=email)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user
