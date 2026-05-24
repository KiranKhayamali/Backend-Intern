from typing import List
from uuid import UUID

from ..repositories.section_repository import SectionRepository
from ..schemas.section import SectionRead, SectionCreate, SectionUpdate
from ..core.exceptions.http_exceptions import NotFoundException, BadRequestException


class SectionService:
    def __init__(self, repo: SectionRepository):
        self.repo = repo

    async def get_all_sections(self) -> List[SectionRead]:
        return await self.repo.get_all_sections()

    async def get_section_by_id(self, section_id: UUID) -> SectionRead:
        try:
            return await self.repo.get_section_by_id(section_id)
        except ValueError as e:
            raise NotFoundException("Section not Found!")

    async def get_section_by_name(self, name: str) -> SectionRead:
        try:
            section = await self.repo.get_section_by_name(name)
            if not section:
                raise NotFoundException(f"{name} section not Found!")
            return section
        except Exception as e:
            raise NotFoundException("Section not Found!")

    async def create_section(self, section_create: SectionCreate) -> SectionRead:
        try:
            return await self.repo.create_section(section_create)
        except ValueError as e:
            raise BadRequestException(str(e))

    async def update_section(self, section_id: UUID, section_update: SectionUpdate) -> SectionRead:
        try:
            updated_section = await self.repo.update_section(section_id, section_update)
            if not updated_section:
                raise NotFoundException("Section not Found!")

            return updated_section
        except ValueError as e:
            raise BadRequestException(str(e))

    async def delete_section(self, section_id: UUID) -> dict:
        try:
            deleted_section = await self.repo.delete_section(section_id)
            if not deleted_section:
                raise NotFoundException("Section not Found!")

            return deleted_section
        except ValueError as e:
            raise NotFoundException(str(e))
        except NotFoundException:
            raise
        except Exception as e:
            raise BadRequestException(str(e))
