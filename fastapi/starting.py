from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None

class User(BaseModel):
    username: str
    full_name: str | None = None

item_db = [
    {"name": "A", "price": 50.2},
    {"name": "B", "price": 100.2},
    {"name": "C", "price": 150.2},
    {"name": "D", "price": 200.2},
    {"name": "E", "price": 250.2},
    {"name": "F", "price": 300.2},
    {"name": "G", "price": 350.2},
    {"name": "H", "price": 400.2},
    {"name": "I", "price": 450.2},
    {"name": "J", "price": 500.2},
    {"name": "K", "price": 550.2},
]



@app.get("/")
def read_root():
    return {"Hello": "World!"}

#Query parameters
@app.get("/items/")
def read_items(skip: int = 0, limit: int = 10):
    return item_db[skip : skip + limit]

@app.get("/items/{item_id}")
def read_item(item_id: int, q: str | None = None):
    if q:   
        return {"item_id": item_id, "q": q}
    return {"item_id": item_id}

# @app.put("/item/{item_id}")
# def update_item(item_id: int, item: Item):
#     return {"item_id": item_id, "item_name": item.name, "item_description": item.description, "item_price": item.price, "item_tax": item.tax}

@app.get("/users/{user_id}/items/{item_id}")
async def read_user_item(
    user_id: int, item_id: str, q: str | None = None, short: bool = False
):
    item = {"item_id": item_id, "owner_id": user_id}
    if q:
        item.update({"q": q})
    if not short:
        item.update(
            {"description": "This is an amazing item that has a long description"}
        )
    return item

@app.post("/items/")
def create_item(item: Item):
    item_dict = item.model_dump()
    if item.tax:
        price_with_tax = item.price + item.tax
        item_dict.update({"price_with_tax": price_with_tax})
    return item_dict

# #Request body + path parameters
# @app.put("/items/{item_id}")
# def update_item(item_id: int, item: Item, q: str | None = None):
#     result = {"item_id": item_id, **item.model_dump()}#** is used to unpack the dictionary returned by model_dump() and merge it with the item_id key-value pair in the returned dictionary.
#     if q:
#         result.update({"q": q})
#     return result

#Multiple body parameters
@app.put("/items/{item_id}")
def update_item(item_id: int, item: Item, user: User):
    return {"item_id": item_id, "item": item, "user": user}