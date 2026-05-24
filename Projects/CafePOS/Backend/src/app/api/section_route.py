from fastapi import APIRouter, Depends, status
from typing import List
from uuid import UUID

from ..core.db.session import SessionDep
from ..schemas.section import SectionRead, SectionCreate, SectionUpdate
from ..services.section_service import SectionService
from ..repositories.section_repository import SectionRepository
from ..dependencies.auth_dependency import get_current_user
from ..schemas.user import UserRead
from ..core.exceptions.http_exceptions import ForbiddenException

section_router = APIRouter(prefix="/sections", tags=["sections"])


def get_section_service(db: SessionDep) -> SectionService:
    return SectionService(repo=SectionRepository(db=db))


@section_router.get("/", response_model=List[SectionRead], status_code=status.HTTP_200_OK)
async def read_all_sections(section_service: SectionService=Depends(get_section_service)):
    return await section_service.get_all_sections()


@section_router.get("/{section_id}", response_model=SectionRead, status_code=status.HTTP_200_OK)
async def read_section_by_id(section_id: UUID, section_service: SectionService=Depends(get_section_service)):
    return await section_service.get_section_by_id(section_id)


@section_router.get("/names/{name}", response_model=SectionRead, status_code=status.HTTP_200_OK)
async def read_section_by_name(name: str, section_service: SectionService=Depends(get_section_service)):
    return await section_service.get_section_by_name(name)


@section_router.post("/", response_model=SectionRead, status_code=status.HTTP_201_CREATED)
async def create_section(section_create: SectionCreate, section_service: SectionService=Depends(get_section_service), current_user: UserRead=Depends(get_current_user)):
    if not current_user.is_admin:
        raise ForbiddenException(detail="Only admin users can create new sections!")

    return await section_service.create_section(section_create)


@section_router.patch("/{section_id}", response_model=SectionRead, status_code=status.HTTP_200_OK)
async def update_section(section_id: UUID, section_update: SectionUpdate, section_service: SectionService=Depends(get_section_service), current_user: UserRead=Depends(get_current_user)):
    if not current_user.is_admin:
        raise ForbiddenException(detail="Only admin users can update sections!")

    return await section_service.update_section(section_id, section_update)


@section_router.delete("/{section_id}", response_model=dict, status_code=status.HTTP_200_OK)
async def delete_section(section_id: UUID, section_service: SectionService=Depends(get_section_service), current_user: UserRead=Depends(get_current_user)):
    if not current_user.is_admin:
        raise ForbiddenException(detail="Only admin users can delete sections!")

    return await section_service.delete_section(section_id)
