from fastapi import APIRouter, Depends, status
from typing import List
from uuid import UUID

from ..core.db.session import SessionDep
from ..schemas.dish import DishRead, DishCreate, DishUpdate
from ..services.dish_service import DishService
from ..repositories.dish_repository import DishRepository
from ..schemas.user import UserRead
from ..dependencies.auth_dependency import get_current_user
from ..core.exceptions.http_exceptions import ForbiddenException

dish_router = APIRouter(prefix="/dishes", tags=["dishes"])


def get_dish_service(db: SessionDep) -> DishService:
    return DishService(repo=DishRepository(db=db))


@dish_router.get("/", response_model=List[DishRead], status_code=status.HTTP_200_OK)
async def read_all_dishes(dish_service: DishService=Depends(get_dish_service)):
    return await dish_service.get_all_dishes()


@dish_router.get("/{dish_id}", response_model=DishRead, status_code=status.HTTP_200_OK)
async def read_dish_by_id(dish_id: UUID, dish_service: DishService=Depends(get_dish_service)):
    return await dish_service.get_dish_by_id(dish_id)


@dish_router.get("/names/{name}", response_model=List[DishRead], status_code=status.HTTP_200_OK)
async def read_dish_by_name(name: str, dish_service: DishService=Depends(get_dish_service)):
    return await dish_service.get_dish_by_name(name)


@dish_router.post("/", response_model=DishRead, status_code=status.HTTP_201_CREATED)
async def create_dish(dish_create: DishCreate, dish_service: DishService=Depends(get_dish_service), current_user: UserRead=Depends(get_current_user)):
    if not current_user.is_admin:
        raise ForbiddenException(detail="Only admins can create dishes!")

    return await dish_service.create_dish(dish_create)


@dish_router.patch("/{dish_id}", response_model=DishRead, status_code=status.HTTP_200_OK)
async def update_dish(dish_id: UUID, dish_update: DishUpdate, dish_service: DishService=Depends(get_dish_service), current_user: UserRead=Depends(get_current_user)):
    if not current_user.is_admin:
        raise ForbiddenException(detail="Only admin users can update dishes!")
    return await dish_service.update_dish(dish_id, dish_update)


@dish_router.delete("/{dish_id}", response_model=dict, status_code=status.HTTP_200_OK)
async def delete_dish(dish_id: UUID, dish_service: DishService=Depends(get_dish_service), current_user: UserRead=Depends(get_current_user)):
    if not current_user.is_admin:
        raise ForbiddenException(detail="Only admin users can delete dishes!")

    return await dish_service.delete_dish(dish_id)
