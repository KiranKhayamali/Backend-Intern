from typing import List
from uuid import UUID

from ..schemas.order import OrderRead, OrderCreate, OrderUpdate
from ..repositories.order_repository import OrderRepository
from ..core.exceptions.http_exceptions import NotFoundException, BadRequestException

class OrderService:
    def __init__(self, repo: OrderRepository):
        self.repo = repo

    async def get_all_orders(self) -> List[OrderRead]:
        orders = await self.repo.get_all_orders()
        return [OrderRead.model_validate(o) for o in orders]

    async def get_order_by_id(self, order_id: UUID) -> OrderRead:
        try:
            order = await self.repo.get_order_by_id(order_id)
            if not order:
                raise NotFoundException("Order not Found!")

            return OrderRead.model_validate(order)
        except NotFoundException:
            raise
        except Exception as e:
            raise BadRequestException(str(e))

    async def create_order(self, order_create: OrderCreate) -> OrderRead:
        try:
            order = await self.repo.create_order(order_create)
            return OrderRead.model_validate(order)
        except ValueError as e:
            if "not Found" in str(e):
                raise NotFoundException(str(e))
            raise BadRequestException(str(e))
        except Exception as e:
            raise BadRequestException(str(e))

    async def update_order(self, order_id: UUID, order_update: OrderUpdate) -> OrderRead:
        try:
            updated_order = await self.repo.update_order(order_id, order_update)
            if not updated_order:
                raise NotFoundException("Order not Found!")

            return OrderRead.model_validate(updated_order)
        except ValueError as e:
            if "not Found" in str(e):
                raise NotFoundException(str(e))

            raise BadRequestException(str(e))
        except Exception as e:
            raise BadRequestException(str(e))

    async def delete_order(self, order_id: UUID) -> dict:
        try:
            deleted_order = await self.repo.delete_order(order_id)
            if not deleted_order:
                raise NotFoundException("Order not Found!")

            return deleted_order
        except ValueError as e:
            if "not found" in str(e).lower():
                raise NotFoundException(str(e))

            raise BadRequestException(str(e))
        except Exception as e:
            raise BadRequestException(str(e))
