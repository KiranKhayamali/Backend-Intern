import asyncio

from sqlalchemy import select

from Projects.CafePOS.Backend.src.app.core.db.database import init_db
from Projects.CafePOS.Backend.src.app.core.db.session import async_session
from Projects.CafePOS.Backend.src.app.core.utils.security import get_password_hash
from Projects.CafePOS.Backend.src.app.models import Bill, BillItem, Dish, Item, Order, Section, Table, User
from Projects.CafePOS.Backend.src.app.models.bills import paymentMethodEnum
from Projects.CafePOS.Backend.src.app.models.items import ItemStatusEnum
from Projects.CafePOS.Backend.src.app.models.orders import OrderStatusEnum
from Projects.CafePOS.Backend.src.app.models.tables import TableStatusEnum
from Projects.CafePOS.Backend.src.app.models.users import RoleEnum


SECTION_DATA = ["Main Dining", "Patio", "Bar Lounge"]

USER_DATA = [
    {
        "first_name": "Sidharth",
        "middle_name": None,
        "last_name": "Sharma",
        "contact_number": "9876543210",
        "password": "Password@123",
        "is_admin": True,
        "role": RoleEnum.receptionist,
    },
    {
        "first_name": "Maya",
        "middle_name": None,
        "last_name": "Thapa",
        "contact_number": "9876543211",
        "password": "Password@123",
        "is_admin": False,
        "role": RoleEnum.waiter,
    },
    {
        "first_name": "Rohan",
        "middle_name": "K",
        "last_name": "Patel",
        "contact_number": "9876543212",
        "password": "Password@123",
        "is_admin": False,
        "role": RoleEnum.chef,
    },
]

TABLE_DATA = [
    {"number": 1, "capacity": 2, "status": TableStatusEnum.available, "section": "Main Dining"},
    {"number": 2, "capacity": 4, "status": TableStatusEnum.occupied, "section": "Main Dining"},
    {"number": 3, "capacity": 4, "status": TableStatusEnum.available, "section": "Main Dining"},
    {"number": 4, "capacity": 6, "status": TableStatusEnum.reserved, "section": "Main Dining"},
    {"number": 5, "capacity": 2, "status": TableStatusEnum.available, "section": "Patio"},
    {"number": 6, "capacity": 4, "status": TableStatusEnum.occupied, "section": "Patio"},
    {"number": 7, "capacity": 4, "status": TableStatusEnum.available, "section": "Bar Lounge"},
    {"number": 8, "capacity": 2, "status": TableStatusEnum.available, "section": "Bar Lounge"},
]

DISH_DATA = [
    {"name": "Espresso", "description": "Double shot espresso with a rich crema.", "price": 180, "category": "Beverage", "dish_type": "Hot Drink"},
    {"name": "Cappuccino", "description": "Espresso with steamed milk and foam.", "price": 220, "category": "Beverage", "dish_type": "Hot Drink"},
    {"name": "Lemon Iced Tea", "description": "Fresh lemon tea served over ice.", "price": 160, "category": "Beverage", "dish_type": "Cold Drink"},
    {"name": "Margherita Pizza", "description": "Tomato, mozzarella, and basil on a thin crust.", "price": 520, "category": "Main Course", "dish_type": "Pizza"},
    {"name": "Grilled Chicken Burger", "description": "Grilled chicken, lettuce, tomato, and house sauce.", "price": 490, "category": "Main Course", "dish_type": "Burger"},
    {"name": "Veg Momos", "description": "Steamed dumplings stuffed with seasoned vegetables.", "price": 260, "category": "Starter", "dish_type": "Snacks"},
    {"name": "Chicken Wings", "description": "Crispy wings tossed in a spicy glaze.", "price": 390, "category": "Starter", "dish_type": "Snacks"},
    {"name": "Caesar Salad", "description": "Romaine, croutons, parmesan, and Caesar dressing.", "price": 340, "category": "Salad", "dish_type": "Light Meal"},
    {"name": "Chocolate Brownie", "description": "Warm brownie served with chocolate sauce.", "price": 210, "category": "Dessert", "dish_type": "Sweet"},
    {"name": "Blueberry Cheesecake", "description": "Creamy cheesecake with blueberry topping.", "price": 260, "category": "Dessert", "dish_type": "Sweet"},
]

ORDER_DATA = [
    {
        "table_number": 2,
        "user_contact": "9876543211",
        "status": OrderStatusEnum.in_progress,
        "remark": "Lunch rush order for a family of four.",
        "items": [
            {"dish": "Margherita Pizza", "quantity": 2, "quantity_type": "piece", "remark": None, "status": ItemStatusEnum.in_progress},
            {"dish": "Lemon Iced Tea", "quantity": 4, "quantity_type": "glass", "remark": "Less sugar", "status": ItemStatusEnum.ready},
            {"dish": "Caesar Salad", "quantity": 1, "quantity_type": "plate", "remark": None, "status": ItemStatusEnum.pending},
        ],
        "bill": {
            "customer_name": "Anita Sharma",
            "customer_contact": "9811122233",
            "payment_method": paymentMethodEnum.card,
        },
    },
    {
        "table_number": 4,
        "user_contact": "9876543210",
        "status": OrderStatusEnum.delivered,
        "remark": "Reserved dinner for a birthday celebration.",
        "items": [
            {"dish": "Grilled Chicken Burger", "quantity": 3, "quantity_type": "plate", "remark": "No onions", "status": ItemStatusEnum.ready},
            {"dish": "Chicken Wings", "quantity": 2, "quantity_type": "plate", "remark": "Extra spicy", "status": ItemStatusEnum.ready},
            {"dish": "Cappuccino", "quantity": 2, "quantity_type": "cup", "remark": None, "status": ItemStatusEnum.ready},
        ],
        "bill": {
            "customer_name": "Sanjay Verma",
            "customer_contact": "9800001122",
            "payment_method": paymentMethodEnum.cash,
        },
    },
    {
        "table_number": 6,
        "user_contact": "9876543211",
        "status": OrderStatusEnum.pending,
        "remark": "Evening drinks and dessert.",
        "items": [
            {"dish": "Espresso", "quantity": 2, "quantity_type": "cup", "remark": None, "status": ItemStatusEnum.pending},
            {"dish": "Chocolate Brownie", "quantity": 2, "quantity_type": "slice", "remark": "Serve warm", "status": ItemStatusEnum.pending},
        ],
        "bill": None,
    },
    {
        "table_number": 7,
        "user_contact": "9876543212",
        "status": OrderStatusEnum.ready,
        "remark": "Prep order for bar service.",
        "items": [
            {"dish": "Blueberry Cheesecake", "quantity": 1, "quantity_type": "slice", "remark": None, "status": ItemStatusEnum.pending},
            {"dish": "Lemon Iced Tea", "quantity": 1, "quantity_type": "glass", "remark": None, "status": ItemStatusEnum.pending},
        ],
        "bill": None,
    },
]


async def _get_existing(session, model, clause):
    return await session.scalar(select(model).where(clause))


async def seed_demo_data() -> None:
    await init_db()

    async with async_session() as session:
        sections_by_name: dict[str, Section] = {}
        for section_name in SECTION_DATA:
            section = await _get_existing(session, Section, Section.name == section_name)
            if section is None:
                section = Section(name=section_name)
                session.add(section)
                await session.flush()
            sections_by_name[section_name] = section

        users_by_contact: dict[str, User] = {}
        for user_data in USER_DATA:
            user = await _get_existing(session, User, User.contact_number == user_data["contact_number"])
            if user is None:
                user = User(
                    first_name=user_data["first_name"],
                    middle_name=user_data["middle_name"],
                    last_name=user_data["last_name"],
                    contact_number=user_data["contact_number"],
                    hashed_password=get_password_hash(user_data["password"]),
                    is_admin=user_data["is_admin"],
                    role=user_data["role"],
                )
                session.add(user)
                await session.flush()
            users_by_contact[user_data["contact_number"]] = user

        dishes_by_name: dict[str, Dish] = {}
        for dish_data in DISH_DATA:
            dish = await _get_existing(session, Dish, Dish.name == dish_data["name"])
            if dish is None:
                dish = Dish(
                    name=dish_data["name"],
                    description=dish_data["description"],
                    price=dish_data["price"],
                    category=dish_data["category"],
                    dish_type=dish_data["dish_type"],
                )
                session.add(dish)
                await session.flush()
            dishes_by_name[dish_data["name"]] = dish

        tables_by_number: dict[int, Table] = {}
        for table_data in TABLE_DATA:
            table = await _get_existing(session, Table, Table.number == table_data["number"])
            if table is None:
                table = Table(
                    number=table_data["number"],
                    capacity=table_data["capacity"],
                    status=table_data["status"],
                    section_id=sections_by_name[table_data["section"]].id,
                )
                session.add(table)
                await session.flush()
            tables_by_number[table_data["number"]] = table

        for order_data in ORDER_DATA:
            table = tables_by_number[order_data["table_number"]]
            user = users_by_contact[order_data["user_contact"]]
            order = await session.scalar(
                select(Order).where(
                    Order.table_id == table.id,
                    Order.user_id == user.id,
                    Order.remark == order_data["remark"],
                )
            )

            if order is None:
                    order = Order(
                        table_id=table.id,
                        user_id=user.id,
                        status=order_data["status"],
                        remark=order_data["remark"],
                    )
            session.add(order)
            await session.flush()

            seeded_order_items: list[tuple[Item, dict[str, object]]] = []
            for item_data in order_data["items"]:
                dish = dishes_by_name[item_data["dish"]]
                item = await session.scalar(
                    select(Item).where(
                        Item.order_id == order.id,
                        Item.dish_id == dish.id,
                        Item.quantity == item_data["quantity"],
                        Item.remark == item_data["remark"],
                    )
                )
                if item is None:
                        item = Item(
                            order_id=order.id,
                            dish_id=dish.id,
                            quantity=item_data["quantity"],
                            quantity_type=item_data["quantity_type"],
                            remark=item_data["remark"],
                            status=item_data["status"],
                        )
                session.add(item)
                await session.flush()
                seeded_order_items.append((item, item_data))

            bill_details = order_data["bill"]
            if bill_details is not None:
                bill = await session.scalar(select(Bill).where(Bill.order_id == order.id))
                if bill is None:
                    total_amount = sum(
                        dishes_by_name[item_data["dish"]].price * item_data["quantity"]
                        for item_data in order_data["items"]
                    )
                    bill = Bill(
                        order_id=order.id,
                        table_id=table.id,
                        user_id=user.id,
                        total_amount=total_amount,
                        customer_name=bill_details["customer_name"],
                        customer_contact=bill_details["customer_contact"],
                        payment_method=bill_details["payment_method"],
                    )
                    session.add(bill)
                    await session.flush()

                    for item, item_data in seeded_order_items:
                        dish = dishes_by_name[item_data["dish"]]
                        bill_item = await session.scalar(
                            select(BillItem).where(
                                BillItem.bill_id == bill.id,
                                BillItem.dish_id == dish.id,
                                BillItem.quantity == item.quantity,
                            )
                        )
                        if bill_item is None:
                            bill_item = BillItem(
                                bill_id=bill.id,
                                dish_id=dish.id,
                                dish_name=dish.name,
                                quantity=item.quantity,
                                unit_price=dish.price,
                                total_price=dish.price * item.quantity,
                            )
                            session.add(bill_item)

        await session.commit()


async def main() -> None:
    await seed_demo_data()
    print("Demo data seeded successfully.")


if __name__ == "__main__":
    asyncio.run(main())