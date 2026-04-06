from typing import Annotated
from fastapi import  Depends, Query, HTTPException, status, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..models import Note, NoteSchema
from ..deps import get_db
from ..auth import get_current_user, get_current_active_user


SessionDep = Annotated[AsyncSession, Depends(get_db)]

router=APIRouter()

@router.get("/")
async def read_notes(db:SessionDep, offset:int = 0, limit: Annotated[int, Query(le=10)] = 10):
    select_sql = select(Note).offset(offset).limit(limit)
    result = await db.execute(select_sql)
    notes = result.scalars().all()
    if not notes:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No Notes on Todo list")
    return notes

@router.get("/{note_id}")
async def read_note(note_id:int, db:SessionDep):
    note = await db.get(Note, note_id)
    if not note:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note Not Found")
    return note

@router.post("/")
async def create_note(note:NoteSchema, db: SessionDep, current_user = Depends(get_current_user)):
    db_note = Note(**note.model_dump(exclude={"id"}), user_id=current_user.id)
    db.add(db_note)
    await db.commit()
    await db.refresh(db_note)
    return db_note

@router.put("/{note_id}")
async def update_note(note_id: int, note:NoteSchema, db:SessionDep, current_user = Depends(get_current_user)):
    note_db = await db.get(Note, note_id)
    if not note_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note Not Found")

    if note_db.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"{current_user.username} is not the owner of the note {note_db.title}")

    existing = await db.execute(
        select(Note).where(
            Note.title == note.title,
            Note.id != note_id
        )
    )
    if existing.scalar():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Title already exists for another note")

    note_db.title = note.title
    note_db.memo = note.memo
    await db.commit()
    await db.refresh(note_db)
    return note_db

@router.delete("/{note_id}")
async def delete_note(note_id:int, db:SessionDep, current_user = Depends(get_current_user)):
    note = await db.get(Note, note_id)
    if not note:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note Not Found")
    if note.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"{current_user.username} is not the owner of the note {note.title}")
    await db.delete(note) 
    await db.commit()
    return {"message": f"{note.title} has been successfully removed from the todo list."}

@router.get("/users/")
async def read_notes_of_current_user(db:SessionDep, offset:int = 0, limit: Annotated[int, Query(le=5)] = 5 , current_user = Depends(get_current_active_user)):
    if current_user.id == Note.user_id:
        select_sql = select(Note).offset(offset).limit(limit)
        result = await db.execute(select_sql)
        notes = result.scalars().all()
        if not notes:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="This user doesn't have any ownership for the notes on the todo list")
        return notes 
    else: 
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not authorized!!!")

@router.get("/users/{user_id}")
async def read_notes_by_user_id(user_id: int, db:SessionDep):
    select_sql = select(Note).where(Note.user_id == user_id)
    result = await db.execute(select_sql)
    notes = result.scalars().all()
    if not notes:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No notes present with the ownership of {user_id}")
    return notes


@router.get("/{note_id}/users/{user_id}")
async def read_note_using_note_id_and_user_id(note_id:int, user_id:int, db:SessionDep):
    note = await db.get(Note, note_id)
    if note.user_id == user_id:
        if not note:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note Not Found!!!")
        return note 
    else:
        print(f"User_id: {user_id}, Note_id: {note_id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User Not Found!!!")