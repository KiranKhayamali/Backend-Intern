from typing import Annotated
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from uuid import UUID

from ..core.schemas import TimestampSchema, UUIDSchema


class DishBase(BaseModel):
    name: Annotated[str, Field(min_length=3, max_length=50, examples=["Momo", "Pizza", "Burger"])]
    description: Annotated[str, Field(max_length=255, examples=["Delicious steamed dumplings", "Cheesy pepperoni pizza", "Juicy beef burger"])] | None = None
    price: Annotated[int, Field(gt=0, examples=[80, 200, 150])]
    category: Annotated[str, Field(max_length=20, examples=["appetizer", "main course", "dessert"])] | None = None
    dish_type: Annotated[str, Field(max_length=20, examples=["veg", "non-veg"])] | None = None


class Dish(DishBase, UUIDSchema, TimestampSchema):
    pass


class DishRead(DishBase):
    model_config = ConfigDict(from_attributes=True)
    id: UUID


class DishCreate(DishBase):
    model_config = ConfigDict(extra="forbid")


class DishCreateInternal(DishCreate):
    pass


class DishUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: Annotated[str, Field(min_length=3, max_length=50, examples=["Momo", "Pizza", "Burger"])] | None = None
    description: Annotated[str, Field(max_length=255, examples=["Delicious steamed dumplings", "Cheesy pepperoni pizza", "Juicy beef burger"])] | None = None
    price: Annotated[int, Field(gt=0, examples=[80, 200, 150])] | None = None
    category: Annotated[str, Field(max_length=20, examples=["appetizer", "main course", "dessert"])] | None = None
    dish_type: Annotated[str, Field(max_length=20, examples=["veg", "non-veg"])] | None = None


class DishUpdateInternal(DishUpdate):
    updated_at: datetime
