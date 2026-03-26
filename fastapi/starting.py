from typing import Annotated

from fastapi import FastAPI, Form, HTTPException, Response
from fastapi.responses import JSONResponse, RedirectResponse
from pydantic import BaseModel, HttpUrl

from fastapi.exception_handlers import(
    http_exception_handler,
    request_validation_exception_handler
)
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

app = FastAPI()

class Image(BaseModel):
    url: HttpUrl #will validate that the value is a valid URL
    name: str

class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None
    tags: set[str] = set()
    image: Image | None = None #Nested models

    model_config = { #model_config is used to add extra info to the output schema, and it will be used in API docs. Also use to add metadata for frontend user interfaces,etc.
        "json_schema_extra": {
            "example":[
                {
                    "item": {
                        "name": "Test",
                        "description": "This is testing part for the postman",
                        "price": 234,
                        "tax": 214,
                        "tags": ["test", "testing", "test"], 
                        "image": {
                            "url": "https://docs.pydantic.dev/latest/",
                            "name": "Pydantic"
                        }
                    },
                    "user":{
                        "username": "Ashura",
                        "fullname": "Kiran Khayamali"
                    }
                }
            ]
        }
    }

class User(BaseModel):
    username: str
    fullname: str | None = None

class FormData(BaseModel):
    username: str
    password: str 
    model_config = {"extra": "forbid"} #extra is used to forbid extra fields in the request body, so if we send any extra fields in the request body, we will get a validation error.

item_db = [
    {"item_id": 1, "name": "A", "price": 50.2},
    {"item_id": 2, "name": "B", "price": 100.2},
    {"item_id": 3, "name": "C", "price": 150.2},
    {"item_id": 4, "name": "D", "price": 200.2},
    {"item_id": 5, "name": "E", "price": 250.2},
    {"item_id": 6, "name": "F", "price": 300.2},
    {"item_id": 7, "name": "G", "price": 350.2},
    {"item_id": 8, "name": "H", "price": 400.2},
    {"item_id": 9, "name": "I", "price": 450.2},
    {"item_id": 10, "name": "J", "price": 500.2},
    {"item_id": 11, "name": "K", "price": 550.2},
]



@app.get("/")
def read_root():
    return {"Hello": "World!"}

#Query parameters
@app.get("/items/")
def read_items(skip: int = 0, limit: int = 10):
    return item_db[skip : skip + limit]

# @app.get("/items/{item_id}")
# async def read_item(item_id: int, q: str | None = None):
#     if item_id not in [item["item_id"] for item in item_db]:
#         print(item_id)
#         raise HTTPException(status_code=404, detail="Item not found")
#     if q:   
#         return {"item_id": item_id, "q": q}
#     return {"item": item_db[item_id - 1]}

@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(request, exc):
    print(f"HTTP exception occurred at {request.url}: {exc.detail}")
    return await http_exception_handler(request, exc)

@app.exception_handler(RequestValidationError)
async def custom_validation_exception_handler(request, exc):
    print(f"Validation error at {request.url}: {exc.errors()}")
    return await request_validation_exception_handler(request, exc)

@app.get("/items/{item_id}")
async def read_item(item_id: int):
    if item_id == 4:
        raise HTTPException(status_code=444, detail= "The 4th item is not available")
    return {"item": item_db[item_id - 1]}


# @app.put("/item/{item_id}")
# def update_item(item_id: int, item: Item):
#     return {"item_id": item_id, "item_name": item.name, "item_description": item.description, "item_price": item.price, "item_tax": item.tax}


#Multiple path and query parameters
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
def create_item(item: Item, user: User | None = None):
    item_dict = item.model_dump()
    if item.tax:
        price_with_tax = item.price + item.tax
        item_dict.update({"price_with_tax": price_with_tax})
    return (item_dict, user if user else None)

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

#Bodies of pure lists
@app.post("/images/multiple/")
async def create_multiple_images(images: list[Image]): #when using def only FastAPI doesn't parse the body properly, and it seem like route "doesn't work" or we get "{detail: "Not Found"}" error, so we need to use async def, and then FastAPI will parse the body properly 
    return images

#Return Response Directly
@app.get("/portal")
async def get_portal(teleport: bool = False) -> Response:
    if teleport:
        return RedirectResponse(url="https://www.youtube.com/watch?v=dQw4w9WgXcQ")
    return JSONResponse(content={"message": "Here's your interdimensional portal."})

#Form Data and model usage 
@app.post("/login/")
async def login(form: Annotated[FormData, Form()]):
    return form