from typing import List
from uuid import UUID

from ..schemas.bill import BillRead, BillCreate, BillUpdate
from ..repositories.bill_repository import BillRepository
from ..core.exceptions.http_exceptions import NotFoundException, BadRequestException, ForbiddenException


class BillService:
    def __init__(self, repo: BillRepository):
        self.repo = repo

    async def get_all_bills(self) -> List[BillRead]:
        bills = await self.repo.get_all_bills()
        return bills

    async def get_bill_by_id(self, bill_id: UUID) -> BillRead:
        try:
            bill = await self.repo.get_bill_by_id(bill_id)
            if not bill:
                raise NotFoundException(f"Bill with ID {bill_id} not Found!")

            return bill
        except(NotFoundException, ForbiddenException):
            raise
        except ValueError as e:
            if "not found" in str(e).lower():
                raise NotFoundException(str(e))

            elif "receptionists and admins" in str(e).lower():
                raise ForbiddenException(str(e))

            raise BadRequestException(str(e))
        except Exception as e:
            raise BadRequestException(str(e))

    async def create_bill(self, bill_create: BillCreate) -> BillRead:
        try:
            bill = await self.repo.create_bill(bill_create)
            if not bill:
                raise NotFoundException("Order not Found!")
            return bill
        except (NotFoundException, ForbiddenException):
            raise
        except ValueError as e:
            if "not found" in str(e).lower():
                raise NotFoundException(str(e))
            elif "receptionists and admins" in str(e).lower():
                raise ForbiddenException(str(e))
            raise BadRequestException(str(e))
        except Exception as e:
            raise BadRequestException(str(e))

    async def update_bill(self, bill_id: UUID, bill_update: BillUpdate) -> BillRead:
        try:
            updated_bill = await self.repo.update_bill(bill_id, bill_update)
            if not updated_bill:
                raise NotFoundException(f"Bill with ID {bill_id} not Found!")

            return updated_bill
        except (NotFoundException, ForbiddenException):
            raise
        except ValueError as e:
            if "not found" or "not found!" in str(e).lower():
                raise NotFoundException(str(e))
            elif "receptionists and admins" in str(e).lower():
                raise ForbiddenException(str(e))
            raise BadRequestException(str(e))
        except Exception as e:
            raise BadRequestException(str(e))

    async def delete_bill(self, bill_id: UUID) -> dict:
        try:
            deleted_bill = await self.repo.delete_bill(bill_id)
            if not deleted_bill:
                raise NotFoundException(f"Bill with ID {bill_id} not Found!")

            return deleted_bill
        except NotFoundException:
            raise
        except ValueError as e:
            if "not found" in str(e).lower():
                raise NotFoundException(str(e))
            elif "receptionists and admins" in str(e).lower():
                raise ForbiddenException(str(e))
            raise BadRequestException(str(e))
        except Exception as e:
            raise BadRequestException(str(e))
