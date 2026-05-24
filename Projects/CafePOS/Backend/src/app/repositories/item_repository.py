from typing import List
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from ..core.db.session import SessionDep
from ..schemas.item import ItemRead, ItemCreate, ItemUpdate
from ..models.items import Item
from ..models.orders import Order
from ..models.dishes import Dish


class ItemRepository:
    def __init__(self, db: SessionDep):
        self.db = db

    async def get_all_items(self) -> List[ItemRead]:
        result = await self.db.execute(select(Item).options(selectinload(Item.dish)))
        items = result.scalars().all()
        return items

    async def get_item_by_id(self, item_id: UUID) -> ItemRead | None:
        result = await self.db.execute(select(Item).where(Item.id == item_id).options(selectinload(Item.dish)))
        item = result.scalar_one_or_none()
        if not item:
            return None

        return item

    async def create_item(self, item_create: ItemCreate) -> ItemRead:
        item_data = item_create.model_dump()

        order_result = await self.db.execute(select(Order).where(Order.id == item_data["order_id"]))
        if not order_result.scalar_one_or_none():
            raise ValueError("Order not Found!")

        dish_result = await self.db.execute(select(Dish).where(Dish.id == item_data["dish_id"]))
        if not dish_result.scalar_one_or_none():
            raise ValueError("Dish not Found!")

        new_item = Item(**item_data)
        self.db.add(new_item)
        await self.db.commit()
        result = await self.db.execute(select(Item).options(selectinload(Item.dish)).where(Item.id == new_item.id))
        created_item = result.scalar_one()
        return created_item

    async def update_item(self, item_id: UUID, item_update: ItemUpdate) -> ItemRead:
        result = await self.db.execute(select(Item).where(Item.id == item_id))
        item = result.scalar_one_or_none()
        if not item:
            raise ValueError("Item not Found!")

        item_data = item_update.model_dump(exclude_unset=True)
        for key, value in item_data.items():
            setattr(item, key, value)

        self.db.add(item)
        await self.db.commit()
        final_result = await self.db.execute(select(Item).options(selectinload(Item.dish)).where(Item.id == item_id))
        updated_item = final_result.scalar_one()
        return updated_item

    async def delete_item(self, item_id: UUID) -> dict:
        result = await self.db.execute(select(Item).where(Item.id == item_id))
        item = result.scalar_one_or_none()
        if not item:
            raise ValueError("Item not Found!")

        await self.db.delete(item)
        await self.db.commit()
        return {"Message": f"Item with id {item_id} has been deleted successfully!"}
