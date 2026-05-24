from typing import List
from uuid import UUID

from ..repositories.table_repository import TableRepository
from ..schemas.table import TableRead, TableCreate, TableUpdate
from ..core.exceptions.http_exceptions import NotFoundException, BadRequestException


class TableService:
    def __init__(self, repo: TableRepository):
        self.repo = repo

    async def get_all_tables(self) -> List[TableRead]:
        return await self.repo.get_all_tables()

    async def get_table_by_id(self, table_id: UUID) -> TableRead:
        try:
            return await self.repo.get_table_by_id(table_id)
        except ValueError as e:
            raise NotFoundException("Table not Found!")

    async def get_table_by_number(self, number: int) -> TableRead:
        try:
            table = await self.repo.get_table_by_number(number)
            if not table:
                raise NotFoundException(f"Table number {number} not Found!")

            return table
        except NotFoundException:
            raise
        except Exception as e:
            raise BadRequestException(f"Error retrieving table by number: {str(e)}")

    async def create_table(self, table_create: TableCreate) -> TableRead:
        try:
            return await self.repo.create_table(table_create)
        except Exception as e:
            raise BadRequestException(str(e))

    async def update_table(self, table_id: UUID, table_update: TableUpdate) -> TableRead:
        try:
            updated_table = await self.repo.update_table(table_id, table_update)
            if not updated_table:
                raise NotFoundException("Table not Found!")

            return updated_table
        except ValueError as e:
            if "not Found" in str(e):
                raise NotFoundException(str(e))
            raise BadRequestException(str(e))

    async def delete_table(self, table_id: UUID) -> dict:
        try:
            deleted_table = await self.repo.delete_table(table_id)
            if not deleted_table:
                raise NotFoundException("Table not Found!")

            return deleted_table
        except ValueError as e:
            if "not Found" in str(e):
                raise NotFoundException(str(e))
            raise BadRequestException(str(e))
