from fastapi import FastAPI
from contextlib import asynccontextmanager
from .core.db.database import async_engine, Base
from .api import notes, users

@asynccontextmanager
async def database_lifespan(app: FastAPI):
    print("App is Starting...........")
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    print("App is Shutting Down........")

app = FastAPI(lifespan=database_lifespan)

@app.get("/")
def root():
    return {"message": "Welcome!! to the ToDo List....."}

#Scaling Todo list with better file structure
app.include_router(users.router, prefix="/users", tags={"Users"})
app.include_router(notes.router, prefix="/notes", tags={"Notes"})