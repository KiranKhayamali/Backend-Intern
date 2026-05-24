from typing import Annotated
from fastapi import  Depends, Query, HTTPException, status, APIRouter
from sqlalchemy import select

from ..schemas.note import NoteRead, NoteCreate, NoteUpdate
from ..models.notes import Note
from ..core.deps import SessionDep
from ..dependencies.auth_dependency import get_current_user
from ..services.note_service import NoteService


router=APIRouter()

def get_note_service(db: SessionDep) -> NoteService:
    return NoteService(db)

@router.get("/")
async def read_notes(notes_service: NoteService = Depends(get_note_service)):
    return await notes_service.get_all_notes()


@router.get("/{note_id}")
async def read_note(note_id:int, notes_service: NoteService = Depends(get_note_service)):
    return await notes_service.get_or_404(note_id)

@router.post("/")
async def create_note(note:NoteCreate, notes_service: NoteService = Depends(get_note_service), current_user = Depends(get_current_user)):
    return await notes_service.create_note(note, current_user.id)

#using is_admin
@router.put("/{note_id}")
async def update_note(note_id: int, note:NoteUpdate, notes_service: NoteService = Depends(get_note_service), current_user = Depends(get_current_user)):
    note_db = await notes_service.get_or_404(note_id)
    if current_user.is_admin == True or note_db.user_id == current_user.id:
        return await notes_service.update_note(note_id, note)
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"{current_user.username} is not the owner of the note {note_db.title}")

@router.delete("/{note_id}")
async def delete_note(note_id:int, notes_service: NoteService = Depends(get_note_service), current_user = Depends(get_current_user)):
    note_db = await notes_service.get_or_404(note_id)
    if current_user.is_admin == True or note_db.user_id == current_user.id:
        await notes_service.delete_note(note_id)
        return {"message": f"{note_db.title} has been successfully removed from the todo list."}
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"{current_user.username} is not the owner of the note {note_db.title}")

# #Comparing Current user ID with the Admin user Id
# @router.put("/{note_id}")
# async def update_note(note_id: int, note:NoteSchema, db:SessionDep, current_user = Depends(get_current_user), admin_user= Depends(get_admin_user)):
#     note_db = await db.get(Note, note_id)
#     if not note_db:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note Not Found")

#     async def update():
#         existing = await db.execute(
#             select(Note).where(
#                 Note.title == note.title,
#                 Note.id != note_id
#             )
#         )
#         if existing.scalar():
#             raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Title already exists for another note")

#         note_db.title = note.title
#         note_db.memo = note.memo
#         await db.commit()
#         await db.refresh(note_db)
#         return note_db
#         # return {f"{note_db.title} has been successfully updated."}


#     if admin_user.id == current_user.id:
#         result = await update()
#         return result
#     elif note_db.user_id == current_user.id:
#         result = await update()
#         return result
#     else:
#         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"{current_user.username} is not the owner of the note {note_db.title}")

# @router.delete("/{note_id}")
# async def delete_note(note_id:int, db:SessionDep, current_user = Depends(get_current_user), admin_user = Depends(get_admin_user)):
#     note = await db.get(Note, note_id)
#     if not note:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note Not Found")
#     if current_user.id == admin_user.id:
#         await db.delete(note)
#         await db.commit()
#         return {"message": f"{note.title} has been successfully removed from the todo list."}

#     elif current_user.id == note.user_id:
#         await db.delete(note)
#         await db.commit()
#         return {"message": f"{note.title} has been successfully removed from the todo list."}
#     else:
#         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"{current_user.username} is not the owner of the note {note.title}")

@router.get("/users/me")
async def read_notes_of_current_user(note_service: NoteService = Depends(get_note_service), current_user = Depends(get_current_user)):
    notes = await note_service.get_notes_by_user_id(current_user.id)
    if not notes:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="This user doesn't have any ownership for the notes on the todo list")
    return notes

@router.get("/users/{user_id}")
async def read_notes_by_user_id(user_id: int, note_service: NoteService = Depends(get_note_service)):
    notes = await note_service.get_notes_by_user_id(user_id)
    if not notes:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No notes present with the ownership of {user_id}")
    return notes

@router.get("/users/")
async def read_note_using_note_id_and_user_id(note_id:int, note_service: NoteService = Depends(get_note_service), current_user = Depends(get_current_user)):
    note = await note_service.get_or_404(note_id)
    if note.user_id == current_user.id:
        return note
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"{current_user.username} is not the owner of the note {note.title}")
