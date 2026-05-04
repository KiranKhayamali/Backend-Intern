from typing import List
from fastapi import HTTPException, status

from ..repositories.note_repository import NoteRepository
from ..schemas.note import NoteRead, NoteCreate, NoteUpdate


class NoteService:
    def __init__(self, db):
        self.repo = NoteRepository(db)

    async def get_all_notes(self) -> List[NoteRead]:
        return await self.repo.get_all()

    async def get_note_by_id(self, note_id: int) -> NoteRead | None:
        return await self.repo.get_by_id(note_id)

    async def get_or_404(self, note_id: int) -> NoteRead:
        note = await self.repo.get_by_id(note_id)
        if not note:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note Not Found")
        return note

    async def get_notes_by_user_id(self, user_id: int) -> List[NoteRead]:
        return await self.repo.get_by_user_id(user_id)

    async def create_note(self, note_data: NoteCreate, user_id: int) -> NoteRead:
        return await self.repo.create(note_data, user_id)

    async def update_note(self, note_id: int, note_data: NoteUpdate) -> NoteRead:
        note = await self.get_or_404(note_id)
        return await self.repo.update(note, note_data)

    async def delete_note(self, note_id: int) -> None:
        note = await self.get_or_404(note_id)
        await self.repo.delete(note)

