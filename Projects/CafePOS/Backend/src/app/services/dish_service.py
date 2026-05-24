from typing import List
from uuid import UUID

from ..repositories.dish_repository import DishRepository
from ..schemas.dish import DishRead, DishCreate, DishUpdate
from ..core.exceptions.http_exceptions import NotFoundException, BadRequestException

class DishService:
    def __init__(self, repo: DishRepository):
        self.repo = repo

    async def get_all_dishes(self) -> List[DishRead]:
        return await self.repo.get_all_dishes()

    async def get_dish_by_id(self, dish_id: UUID) -> DishRead:
        try:
            return await self.repo.get_dish_by_id(dish_id)
        except ValueError as e:
            raise NotFoundException("Dish not Found!")

    async def get_dish_by_name(self, name: str) -> DishRead:
        try:
            return await self.repo.get_dish_by_name(name)
        except ValueError as e:
            raise NotFoundException("Dish not Found!")

    async def create_dish(self, dish_create: DishCreate) -> DishRead:
        try:
            return await self.repo.create_dish(dish_create)
        except Exception as e:
            raise BadRequestException(str(e))

    async def update_dish(self, dish_id: UUID, dish_update: DishUpdate) -> DishRead:
        try:
            updated_dish = await self.repo.update_dish(dish_id, dish_update)
            if not updated_dish:
                raise NotFoundException("Dish not Found!")

            return updated_dish
        except ValueError as e:
            if "not found" in str(e).lower():
                raise NotFoundException(str(e))

            raise BadRequestException(str(e))
        except Exception as e:
            raise BadRequestException(str(e))

    async def delete_dish(self, dish_id: UUID) -> dict:
        try:
            deleted_dish = await self.repo.delete_dish(dish_id)
            if not deleted_dish:
                raise NotFoundException("Dish not Found!")

            return deleted_dish
        except ValueError as e:
            if "not found" in str(e).lower():
                raise NotFoundException(str(e))

            raise BadRequestException(str(e))
        except Exception as e:
            raise BadRequestException(str(e))