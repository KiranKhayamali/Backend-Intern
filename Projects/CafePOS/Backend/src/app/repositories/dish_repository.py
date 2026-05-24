from typing import List
from sqlalchemy import select
from uuid import UUID

from ..core.db.session import SessionDep
from ..models.dishes import Dish
from ..schemas.dish import DishRead, DishCreate, DishUpdate


class DishRepository:
    def __init__(self, db: SessionDep):
        self.db = db

    async def get_all_dishes(self) -> List[DishRead]:
        result = await self.db.execute(select(Dish))
        dishes = result.scalars().all()
        return dishes

    async def get_dish_by_id(self, dish_id: UUID) -> DishRead:
        result = await self.db.execute(select(Dish).where(Dish.id == dish_id))
        dish = result.scalar_one_or_none()
        if not dish:
            raise ValueError("Dish not Found!")

        return dish

    async def get_dish_by_name(self, name: str) -> List[DishRead]:
        result = await self.db.execute(select(Dish).where(Dish.name == name))
        dish = result.scalars().all()
        if not dish:
            raise ValueError("Dish not Found!")

        return dish

    async def create_dish(self, dish_create: DishCreate) -> DishRead:
        dish_data = dish_create.model_dump()
        new_dish = Dish(**dish_data)
        self.db.add(new_dish)
        await self.db.commit()
        await self.db.refresh(new_dish)
        return new_dish

    async def update_dish(self, dish_id: UUID, dish_update: DishUpdate) -> DishRead:
        result = await self.db.execute(select(Dish).where(Dish.id == dish_id))
        dish = result.scalar_one_or_none()
        if not dish:
            raise ValueError("Dish not Found!")

        dish_data = dish_update.model_dump(exclude_unset=True)
        for key, value in dish_data.items():
            setattr(dish, key, value)

        self.db.add(dish)
        await self.db.commit()
        await self.db.refresh(dish)
        return dish

    async def delete_dish(self, dish_id: UUID) -> dict:
        result = await self.db.execute(select(Dish).where(Dish.id == dish_id))
        dish = result.scalar_one_or_none()
        if not dish:
            raise ValueError("Dish not Found!")

        await self.db.delete(dish)
        await self.db.commit()
        return {"Message": f"{dish.name} has been successfully deleted!"}

