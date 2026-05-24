from fastapi import APIRouter, Depends, status
from typing import List
from uuid import UUID

from ..core.db.session import SessionDep
from ..schemas.table import TableRead, TableCreate, TableUpdate
from ..services.table_service import TableService
from ..repositories.table_repository import TableRepository
from ..dependencies.auth_dependency import get_current_user
from ..schemas.user import UserRead
from ..core.exceptions.http_exceptions import ForbiddenException

table_router = APIRouter(prefix="/tables", tags=["tables"])


def get_table_service(db: SessionDep) -> TableService:
    return TableService(repo=TableRepository(db=db))


@table_router.get("/", response_model=List[TableRead], status_code=status.HTTP_200_OK)
async def read_all_tables(table_service: TableService=Depends(get_table_service)):
    return await table_service.get_all_tables()


@table_router.get("/{table_id}", response_model=TableRead, status_code=status.HTTP_200_OK)
async def read_table_by_id(table_id: UUID, table_service: TableService=Depends(get_table_service)):
    return await table_service.get_table_by_id(table_id)


@table_router.get("/numbers/{number}", response_model=TableRead, status_code=status.HTTP_200_OK)
async def read_table_by_number(number: int, table_service: TableService=Depends(get_table_service)):
    return await table_service.get_table_by_number(number)


@table_router.post("/", response_model=TableRead, status_code=status.HTTP_201_CREATED)
async def create_table(table_create: TableCreate, table_service: TableService=Depends(get_table_service), current_user: UserRead=Depends(get_current_user)):
    if not current_user.is_admin:
        raise ForbiddenException(detail="Only admin users can create new tables!")

    return await table_service.create_table(table_create)


@table_router.patch("/{table_id}", response_model=TableRead, status_code=status.HTTP_200_OK)
async def update_table(table_id: UUID, table_update: TableUpdate, table_service: TableService=Depends(get_table_service), current_user: UserRead=Depends(get_current_user)):
    if not current_user.is_admin:
        raise ForbiddenException(detail="Only admin users can update tables!")

    return await table_service.update_table(table_id, table_update)


@table_router.delete("/{table_id}", response_model=dict, status_code=status.HTTP_200_OK)
async def delete_table(table_id: UUID, table_service: TableService=Depends(get_table_service), current_user: UserRead=Depends(get_current_user)):
    if not current_user.is_admin:
        raise ForbiddenException(detail="Only admin users can delete tables!")

    return await table_service.delete_table(table_id)
