from typing import List
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from uuid import UUID

from ..core.db.session import SessionDep
from ..schemas.table import TableRead, TableCreate, TableUpdate
from ..models.tables import Table


class TableRepository:
    def __init__(self, db: SessionDep):
        self.db = db

    async def get_all_tables(self) -> List[TableRead]:
        result = await self.db.execute(select(Table).options(selectinload(Table.section)))
        tables = result.scalars().all()
        return tables

    async def get_table_by_id(self, table_id: UUID) -> TableRead:
        result = await self.db.execute(select(Table).where(Table.id == table_id).options(selectinload(Table.section)))
        table = result.scalar_one_or_none()
        if not table:
            raise ValueError("Table not Found!")

        return table

    async def get_table_by_number(self, number: int) -> TableRead | None:
        result = await self.db.execute(select(Table).where(Table.number == number).options(selectinload(Table.section)))
        table = result.scalar_one_or_none()
        if not table:
            return None

        return table

    async def create_table(self, table_create: TableCreate) -> TableRead:
        existing_table = await self.get_table_by_number(table_create.number)
        if existing_table:
            raise ValueError(f"Table with number {table_create.number} already exists!")

        table_data = table_create.model_dump()
        new_table = Table(**table_data)
        self.db.add(new_table)
        await self.db.commit()
        await self.db.refresh(new_table)
        return new_table

    async def update_table(self, table_id: UUID, table_update: TableUpdate) -> TableRead:
        result = await self.db.execute(select(Table).where(Table.id == table_id))
        table = result.scalar_one_or_none()
        if not table:
            raise ValueError("Table not Found!")

        table_data = table_update.model_dump(exclude_unset=True)
        for key, value in table_data.items():
            setattr(table, key, value)

        await self.db.commit()
        await self.db.refresh(table)
        return table

    async def delete_table(self, table_id: UUID) -> dict:
        result = await self.db.execute(select(Table).where(Table.id == table_id))
        table = result.scalar_one_or_none()
        if not table:
            raise ValueError("Table not Found!")

        await self.db.delete(table)
        await self.db.commit()
        return {"Message": f"Table {table.number} has been successfully deleted!"}
