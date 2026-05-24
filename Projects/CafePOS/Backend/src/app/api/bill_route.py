from fastapi import APIRouter, Depends, status
from typing import List
from uuid import UUID

from ..core.db.session import SessionDep
from ..dependencies.auth_dependency import get_current_user
from ..schemas.bill import BillRead, BillCreate, BillUpdate
from ..services.bill_service import BillService
from ..repositories.bill_repository import BillRepository
from ..models.users import User
from ..core.exceptions.http_exceptions import ForbiddenException

bill_router = APIRouter(prefix="/bills", tags=["bills"], dependencies=[Depends(get_current_user)])


def get_bill_service(db: SessionDep) -> BillService:
    return BillService(repo=BillRepository(db=db))


@bill_router.get("/", response_model=List[BillRead], status_code=status.HTTP_200_OK)
async def read_all_bills(bill_service: BillService=Depends(get_bill_service), current_user: User = Depends(get_current_user)):
    if not (getattr(current_user, "role", "") == "receptionist" or getattr(current_user, "is_admin", False)):
        raise ForbiddenException(detail="Only receptionists and admins can access bills!")

    return await bill_service.get_all_bills()


@bill_router.get("/{bill_id}", response_model=BillRead, status_code=status.HTTP_200_OK)
async def read_bill_by_id(bill_id: UUID, bill_service: BillService=Depends(get_bill_service), current_user: User = Depends(get_current_user)):
    if not (getattr(current_user, "is_admin", False) or getattr(current_user, "role", "") == "receptionist"):
        raise ForbiddenException(detail="Only receptionists and admins can access bill details!")

    return await bill_service.get_bill_by_id(bill_id)


@bill_router.post("/", response_model=BillRead, status_code=status.HTTP_201_CREATED)
async def create_bill(bill_create: BillCreate, bill_service: BillService=Depends(get_bill_service)):
    return await bill_service.create_bill(bill_create)


@bill_router.patch("/{bill_id}", response_model=BillRead, status_code=status.HTTP_200_OK)
async def update_bill(bill_id: UUID, bill_update: BillUpdate, bill_service: BillService=Depends(get_bill_service), current_user: User = Depends(get_current_user)):
    # Only receptionists and admins can update bills
    if not (getattr(current_user, "is_admin", False) or getattr(current_user, "role", "") == "receptionist"):
        raise ForbiddenException(detail="Only receptionists and admins can update bills!")

    return await bill_service.update_bill(bill_id, bill_update)


@bill_router.delete("/{bill_id}", response_model=dict, status_code=status.HTTP_200_OK)
async def delete_bill(bill_id: UUID, bill_service: BillService=Depends(get_bill_service), current_user: User = Depends(get_current_user)):
    if not (getattr(current_user, "is_admin", False) or getattr(current_user, "role", "") == "receptionist"):
        raise ForbiddenException(detail="Only receptionists and admins can delete bills!")
    return await bill_service.delete_bill(bill_id)
