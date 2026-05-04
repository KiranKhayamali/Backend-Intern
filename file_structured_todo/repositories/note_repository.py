from typing import List
from sqlalchemy import select

from ..core.deps import SessionDep
from ..models.notes import Note
from ..schemas.note import NoteRead, NoteCreate, NoteUpdate


class NoteRepository:
    def __init__(self, db:SessionDep):
        self.db = db

    async def get_all(self) -> List[NoteRead]:
        result = await self.db.execute(select(Note))
        notes = result.scalars().all()
        return notes

    async def get_by_id(self, note_id: int) -> NoteRead | None:
        note = await self.db.get(Note, note_id)
        return note

    async def get_by_user_id(self, user_id: int) -> List[NoteRead]:
        result = await self.db.execute(select(Note).where(Note.user_id == user_id))
        notes = result.scalars().all()
        return notes

    async def create(self, note_data: NoteCreate, user_id: int) -> NoteRead:
        db_note = Note(**note_data.model_dump(exclude={"id"}), user_id=user_id)
        self.db.add(db_note)
        await self.db.commit()
        await self.db.refresh(db_note)
        return db_note

    async def update(self, note:Note, note_data:NoteUpdate) -> NoteRead:
        update_data = note_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(note, key, value)
        await self.db.commit()
        await self.db.refresh(note)
        return note

    async def delete(self, note:Note) -> None:
        await self.db.delete(note)
        await self.db.commit()