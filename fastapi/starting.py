from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Item(BaseModel):
    name: str
    description: str = None
    price: float
    tax: float = None

@app.get("/")
def read_root():
    return {"Hello": "World!"}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: str = None):
    return {"item_id": item_id, "q": q}

@app.put("/item/{item_id}")
def update_item(item_id: int, item: Item):
    return {"item_id": item_id, "item_name": item.name, "item_description": item.description, "item_price": item.price, "item_tax": item.tax}