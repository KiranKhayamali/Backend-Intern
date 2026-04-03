from typing import Annotated
from fastapi import FastAPI, Depends, Query, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager
from models import Note, NoteSchema, Base
from database import engine
from deps import get_db


SessionDep = Annotated[AsyncSession, Depends(get_db)]

@asynccontextmanager
async def database_lifespan(app: FastAPI):
    print("App is Starting...........")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    print("App is Shutting Down........")

app = FastAPI(lifespan=database_lifespan)

@app.get("/")
def root():
    return {"message": "Welcome!! to the ToDo List....."}

@app.get("/notes/")
async def read_notes(db:SessionDep, offset:int = 0, limit: Annotated[int, Query(le=10)] = 10):
    select_sql = select(Note).offset(offset).limit(limit)
    result = await db.execute(select_sql)
    notes = result.scalars().all()
    return notes


@app.post("/notes/")
async def create_note(note:NoteSchema, db: SessionDep):
    db_note = Note(**note.model_dump())
    db.add(db_note)
    await db.commit()
    await db.refresh(db_note)
    return db_note

@app.put("/notes/{note_id}")
async def update_note(note_id: int, note:NoteSchema, db:SessionDep):
    note_db = await db.get(Note, note_id)
    if not note_db:
        db_note = Note(**note.model_dump())
        db.add(db_note)
        await db.commit()
        await db.refresh(db_note)
        return {"message": f"{db_note.title} has been created to the todo list."} 

    existing = await db.execute(
        select(Note).where(
            Note.title == note.title,
            Note.id != note_id
        )
    )
    if existing.scalar():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Title doesn't exists on {note_id} in the database")

    if note_db.title== note.title:
        note_db.memo = note.memo
    await db.commit()
    await db.refresh(note_db)
    return note_db

@app.delete("/notes/{note_id}")
async def delete_note(note_id:int, db:SessionDep):
    note = await db.get(Note, note_id)
    if not note:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note Not Found")
    await db.delete(note) 
    await db.commit()
    return {"message": f"{note.title} has been successfully removed from the todo list."}