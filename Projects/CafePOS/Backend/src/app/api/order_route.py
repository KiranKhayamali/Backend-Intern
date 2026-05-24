from fastapi import APIRouter, Depends, status
from typing import List
from uuid import UUID

from ..core.db.session import SessionDep
from ..schemas.order import OrderRead, OrderCreate, OrderUpdate
from ..services.order_service import OrderService
from ..repositories.order_repository import OrderRepository

order_router = APIRouter(prefix="/orders", tags=["orders"])


def get_order_service(db: SessionDep) -> OrderService:
    return OrderService(repo=OrderRepository(db=db))


@order_router.get("/", response_model=List[OrderRead], status_code=status.HTTP_200_OK)
async def read_all_orders(order_service: OrderService=Depends(get_order_service)):
    return await order_service.get_all_orders()


@order_router.get("/{order_id}", response_model=OrderRead, status_code=status.HTTP_200_OK)
async def read_order_by_id(order_id: UUID, order_service: OrderService=Depends(get_order_service)):
    return await order_service.get_order_by_id(order_id)


@order_router.post("/", response_model=OrderRead, status_code=status.HTTP_201_CREATED)
async def create_order(order_create: OrderCreate, order_service: OrderService=Depends(get_order_service)):
    return await order_service.create_order(order_create)


@order_router.patch("/{order_id}", response_model=OrderRead, status_code=status.HTTP_200_OK)
async def update_order(order_id: UUID, order_update: OrderUpdate, order_service: OrderService=Depends(get_order_service)):
    return await order_service.update_order(order_id, order_update)


@order_router.delete("/{order_id}", response_model=dict, status_code=status.HTTP_200_OK)
async def delete_order(order_id: UUID, order_service: OrderService=Depends(get_order_service)):
    return await order_service.delete_order(order_id)
