from fastapi import APIRouter, Depends, status
from typing import List
from uuid import UUID

from ..core.db.session import SessionDep
from ..schemas.item import ItemRead, ItemCreate, ItemUpdate
from ..services.item_service import ItemService
from ..repositories.item_repository import ItemRepository

item_router = APIRouter(prefix="/items", tags=["items"])


def get_item_service(db: SessionDep) -> ItemService:
    return ItemService(repo=ItemRepository(db=db))


@item_router.get("/", response_model=List[ItemRead], status_code=status.HTTP_200_OK)
async def read_all_items(item_service: ItemService=Depends(get_item_service)):
    return await item_service.get_all_items()


@item_router.get("/{item_id}", response_model=ItemRead, status_code=status.HTTP_200_OK)
async def read_item_by_id(item_id: UUID, item_service: ItemService=Depends(get_item_service)):
    return await item_service.get_item_by_id(item_id)


@item_router.post("/", response_model=ItemRead, status_code=status.HTTP_201_CREATED)
async def create_item(item_create: ItemCreate, item_service: ItemService=Depends(get_item_service)):
    return await item_service.create_item(item_create)


@item_router.patch("/{item_id}", response_model=ItemRead, status_code=status.HTTP_200_OK)
async def update_item(item_id: UUID, item_update: ItemUpdate, item_service: ItemService=Depends(get_item_service)):
    return await item_service.update_item(item_id, item_update)


@item_router.delete("/{item_id}", response_model=dict, status_code=status.HTTP_200_OK)
async def delete_item(item_id: UUID, item_service: ItemService=Depends(get_item_service)):
    return await item_service.delete_item(item_id)
