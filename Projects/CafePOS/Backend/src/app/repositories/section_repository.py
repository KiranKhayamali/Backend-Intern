from typing import List
from sqlalchemy import select
from uuid import UUID

from ..core.db.session import SessionDep
from ..schemas.section import SectionRead, SectionCreate, SectionUpdate
from ..models.sections import Section


class SectionRepository:
    def __init__(self, db: SessionDep):
        self.db = db

    async def get_all_sections(self) -> List[SectionRead]:
        result = await self.db.execute(select(Section))
        sections = result.scalars().all()
        return sections

    async def get_section_by_id(self, section_id: UUID) -> SectionRead :
        result = await self.db.execute(select(Section).where(Section.id == section_id))
        section = result.scalar_one_or_none()
        if not section:
            raise ValueError("Section not Found!")

        return section

    async def get_section_by_name(self, name: str) -> SectionRead | None:
        result = await self.db.execute(select(Section).where(Section.name == name))
        section = result.scalar_one_or_none()
        if not section:
            return None

        return section

    async def create_section(self, section_create: SectionCreate) -> SectionRead:
        existing_section = await self.get_section_by_name(section_create.name)
        if existing_section:
            raise ValueError(f"{section_create.name} already exists!")

        section_data = section_create.model_dump()
        new_section = Section(**section_data)
        self.db.add(new_section)
        await self.db.commit()
        await self.db.refresh(new_section)
        return new_section

    async def update_section(self, section_id: UUID, section_update: SectionUpdate) -> SectionRead | None:
        result = await self.db.execute(select(Section).where(Section.id == section_id))
        section = result.scalar_one_or_none()
        if not section:
            return None

        section_data = section_update.model_dump(exclude_unset=True)
        for key, value in section_data.items():
            setattr(section, key, value)

        await self.db.commit()
        await self.db.refresh(section)
        return section

    async def delete_section(self, section_id: UUID) -> dict:
        result = await self.db.execute(select(Section).where(Section.id == section_id))
        section = result.scalar_one_or_none()
        if not section:
            return None

        await self.db.delete(section)
        await self.db.commit()
        return {"Message": f"{section.name} has been successfully deleted!"}
