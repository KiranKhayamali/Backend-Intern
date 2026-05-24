from typing import List
from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload
from uuid import UUID

from ..core.db.session import SessionDep
from ..schemas.bill import BillRead, BillCreate, BillUpdate
from ..models.bills import Bill, paymentMethodEnum
from ..models.bill_items import BillItem
from ..models.orders import Order
from ..models.items import Item
from ..models.tables import Table
from ..models.users import User


class BillRepository:
    def __init__(self, db: SessionDep):
        self.db = db

    async def get_all_bills(self) -> List[BillRead]:
        result = await self.db.execute(select(Bill).options(
            selectinload(Bill.items),
            selectinload(Bill.table).selectinload(Table.section),
            selectinload(Bill.user)
        ))
        bills = result.scalars().all()
        return bills

    async def get_bill_by_id(self, bill_id: UUID) -> BillRead | None:
        result = await self.db.execute(select(Bill).options(
            selectinload(Bill.items),
            selectinload(Bill.table).selectinload(Table.section),
            selectinload(Bill.user)).where(Bill.id == bill_id))
        bill = result.scalar_one_or_none()
        if not bill:
            return None

        return bill

    async def create_bill(self, bill_create: BillCreate) -> BillRead:
        bill_data = bill_create.model_dump()

        table_result = await self.db.execute(select(Table).where(Table.id == bill_create.table_id))
        table = table_result.scalar_one_or_none()
        if not table:
            raise ValueError("Table not Found!")

        user_result = await self.db.execute(select(User).where(User.id == bill_create.user_id))
        user = user_result.scalar_one_or_none()
        if not user:
            raise ValueError("User not Found!")

        if user.role != "receptionist" and not user.is_admin:
            raise ValueError("Only receptionists and admins can create bills!")

        order_result = await self.db.execute(
            select(Order)
            .options(selectinload(Order.items).selectinload(Item.dish))
            .where(Order.id == bill_create.order_id)
        )
        order = order_result.scalar_one_or_none()
        if not order:
            raise ValueError(f"Order with id {bill_create.order_id} not found")

        if not order.items:
            raise ValueError("Cannot create bill because order has no items")

        bill_data["total_amount"] = 0
        new_bill = Bill(**bill_data)
        self.db.add(new_bill)
        await self.db.flush()

        total_amount = 0
        for order_item in order.items:
            if not order_item.dish:
                raise ValueError(f"Dish with id {order_item.dish_id} not found for item {order_item.id}")

            total_price = order_item.quantity * order_item.dish.price
            total_amount += total_price

            bill_item = BillItem(
                bill_id=new_bill.id,
                dish_id=order_item.dish_id,
                dish_name=order_item.dish.name,
                quantity=order_item.quantity,
                unit_price=order_item.dish.price,
                total_price=total_price,
            )
            self.db.add(bill_item)

        new_bill.total_amount = total_amount

        await self.db.commit()

        result = await self.db.execute(select(Bill).options(
            selectinload(Bill.items),
            selectinload(Bill.table).selectinload(Table.section),
            selectinload(Bill.user)
        ).where(Bill.id == new_bill.id))
        created_bill = result.scalar_one()
        return created_bill

    async def update_bill(self, bill_id: UUID, bill_update: BillUpdate) -> BillRead:
        result = await self.db.execute(select(Bill).where(Bill.id == bill_id))
        bill = result.scalar_one_or_none()
        if not bill:
            raise ValueError("Bill not Found!")

        bill_data = bill_update.model_dump(exclude_unset=True)

        # Validate table and user only if they are present in the update payload
        if "table_id" in bill_data:
            table_result = await self.db.execute(select(Table).where(Table.id == bill_data["table_id"]))
            table = table_result.scalar_one_or_none()
            if not table:
                raise ValueError("Table not Found!")

        if "user_id" in bill_data:
            user_result = await self.db.execute(select(User).where(User.id == bill_data["user_id"]))
            user = user_result.scalar_one_or_none()
            if not user:
                raise ValueError("User not Found!")

            if user.role != "receptionist" and not user.is_admin:
                raise ValueError("Only receptionists and admins can update bills!")

        # Apply simple attribute updates only after validation succeeds.
        for key, value in bill_data.items():
            if key in {"order_id", "table_id", "user_id"}:
                continue

            if key == "payment_method" and isinstance(value, str):
                try:
                    value = paymentMethodEnum(value)
                except ValueError:
                    raise ValueError(f"Invalid payment method: {value}")

            setattr(bill, key, value)

        if "table_id" in bill_data:
            bill.table_id = bill_data["table_id"]

        if "user_id" in bill_data:
            bill.user_id = bill_data["user_id"]


        # If order_id changes, rebuild bill_items and recalculate total_amount from the new order.
        if "order_id" in bill_data and bill_data["order_id"] != bill.order_id:
            new_order_id = bill_data["order_id"]
            order_result = await self.db.execute(
                select(Order)
                .options(selectinload(Order.items).selectinload(Item.dish))
                .where(Order.id == new_order_id)
            )
            order = order_result.scalar_one_or_none()
            if not order:
                raise ValueError(f"Order with id {new_order_id} not found")
            if not order.items:
                raise ValueError("Cannot update bill because selected order has no items")

            await self.db.execute(delete(BillItem).where(BillItem.bill_id == bill.id))

            total_amount = 0
            for order_item in order.items:
                if not order_item.dish:
                    raise ValueError(f"Dish with id {order_item.dish_id} not found for item {order_item.id}")

                total_price = order_item.quantity * order_item.dish.price
                total_amount += total_price

                self.db.add(
                    BillItem(
                        bill_id=bill.id,
                        dish_id=order_item.dish_id,
                        dish_name=order_item.dish.name,
                        quantity=order_item.quantity,
                        unit_price=order_item.dish.price,
                        total_price=total_price,
                    )
                )

            bill.order_id = new_order_id
            bill.total_amount = total_amount

            if "order_id" in bill_data:
                bill.order_id = bill_data["order_id"]

        await self.db.commit()
        refreshed_result = await self.db.execute(
            select(Bill).options(
                selectinload(Bill.items),
                selectinload(Bill.table).selectinload(Table.section),
                selectinload(Bill.user)
            ).where(Bill.id == bill.id)
        )
        refreshed_bill = refreshed_result.scalar_one()
        return refreshed_bill

    async def delete_bill(self, bill_id: UUID) -> dict:
        result = await self.db.execute(select(Bill).where(Bill.id == bill_id))
        bill = result.scalar_one_or_none()
        if not bill:
            raise ValueError("Bill not Found!")

        await self.db.delete(bill)
        await self.db.commit()
        return {"Message": f"Bill with id {bill_id} has been deleted successfully!"}
