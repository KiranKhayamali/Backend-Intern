from typing import List
from uuid import UUID

from ..schemas.item import ItemRead, ItemCreate, ItemUpdate
from ..repositories.item_repository import ItemRepository
from ..core.exceptions.http_exceptions import NotFoundException, BadRequestException


class ItemService:
    def __init__(self, repo: ItemRepository):
        self.repo = repo

    async def get_all_items(self) -> List[ItemRead]:
        return await self.repo.get_all_items()

    async def get_item_by_id(self, item_id: UUID) -> ItemRead:
        try:
            item = await self.repo.get_item_by_id(item_id)
            if not item:
                raise NotFoundException("Item not Found!")

            return item
        except ValueError as e:
            if "not found" in str(e).lower():
                raise NotFoundException(str(e))

            raise BadRequestException(str(e))
        except Exception as e:
            raise NotFoundException("Item not Found!")

    async def create_item(self, item_create: ItemCreate) -> ItemRead:
        try:
            return await self.repo.create_item(item_create)
        except ValueError as e:
            if "not found" in str(e).lower():
                raise NotFoundException(str(e))

            raise BadRequestException(str(e))
        except Exception as e:
            raise BadRequestException(str(e))

    async def update_item(self, item_id: UUID, item_update: ItemUpdate) -> ItemRead:
        try:
            updated_item = await self.repo.update_item(item_id, item_update)
            if not updated_item:
                raise NotFoundException("Item not Found!")

            return updated_item
        except ValueError as e:
            if "not found" in str(e).lower():
                raise NotFoundException(str(e))

            raise BadRequestException(str(e))
        except Exception as e:
            raise BadRequestException(str(e))

    async def delete_item(self, item_id: UUID) -> dict:
        try:
            deleted_item = await self.repo.delete_item(item_id)
            if not deleted_item:
                raise NotFoundException("Item not Found!")

            return deleted_item
        except ValueError as e:
            if "not found" in str(e).lower():
                raise NotFoundException(str(e))

            raise BadRequestException(str(e))
        except Exception as e:
            raise BadRequestException(str(e))
