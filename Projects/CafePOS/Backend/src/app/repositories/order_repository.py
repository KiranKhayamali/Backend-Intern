from typing import List
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from ..core.db.session import SessionDep
from ..schemas.order import OrderRead, OrderCreate, OrderUpdate
from ..models.orders import Order
from ..models.items import Item
from ..models.tables import Table
from ..models.users import User


class OrderRepository:
    def __init__(self, db: SessionDep):
        self.db = db

    async def get_all_orders(self) -> List[OrderRead]:
        result = await self.db.execute(
            select(Order).options(
                selectinload(Order.items).selectinload(Item.dish),
                selectinload(Order.table).selectinload(Table.section),
                selectinload(Order.user)
            )
        )
        orders = result.scalars().all()
        return orders

    async def get_order_by_id(self, order_id: UUID) -> OrderRead | None:
        result = await self.db.execute(
            select(Order).options(
                selectinload(Order.items).selectinload(Item.dish),
                selectinload(Order.table).selectinload(Table.section),
                selectinload(Order.user)
            ).where(Order.id == order_id)
        )
        order = result.scalar_one_or_none()
        if not order:
            return None

        return order

    async def create_order(self, order_create: OrderCreate) -> OrderRead:
        order_data = order_create.model_dump()

        table_result = await self.db.execute(select(Table).where(Table.id == order_data["table_id"]))
        if not table_result.scalar_one_or_none():
            raise ValueError("Table not Found!")

        user_result = await self.db.execute(select(User).where(User.id == order_data["user_id"]))
        if not user_result.scalar_one_or_none():
            raise ValueError("User not Found!")

        new_order = Order(**order_data)
        self.db.add(new_order)
        await self.db.commit()
        # load the order back with items and nested relationships eagerly loaded to avoid lazy async IO later
        result = await self.db.execute(
            select(Order).options(
                selectinload(Order.items).selectinload(Item.dish),
                selectinload(Order.table).selectinload(Table.section),
                selectinload(Order.user)
            ).where(Order.id == new_order.id)
        )
        created = result.scalar_one()
        return created

    async def update_order(self, order_id: UUID, order_update: OrderUpdate) -> OrderRead:
        result = await self.db.execute(select(Order).where(Order.id == order_id))
        order = result.scalar_one_or_none()
        if not order:
            raise ValueError("Order not Found!")

        order_data = order_update.model_dump(exclude_unset=True)
        for key, value in order_data.items():
            setattr(order, key, value)

        await self.db.commit()
        # return fully loaded order with items and nested relationships
        result = await self.db.execute(
            select(Order).options(
                selectinload(Order.items).selectinload(Item.dish),
                selectinload(Order.table).selectinload(Table.section),
                selectinload(Order.user)
            ).where(Order.id == order_id)
        )
        updated = result.scalar_one()
        return updated

    async def delete_order(self, order_id: UUID) -> dict:
        result = await self.db.execute(select(Order).where(Order.id == order_id))
        order = result.scalar_one_or_none()
        if not order:
            raise ValueError("Order not Found!")

        await self.db.delete(order)
        await self.db.commit()
        return {"Message": "Order has been deleted successfully!"}
