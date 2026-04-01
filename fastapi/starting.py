from typing import Annotated

from fastapi import Cookie, Depends, FastAPI, Form, HTTPException, Response
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

user_db = [
    {"username": "Ashura", "fullname": "Kiran Khayamali"},
    {"username": "JohnDoe", "fullname": "John Doe"},
]

#Class as Dependency
class dependency_skip():
    def __init__(self, q: str| None = None, skip: int = 0, limit: int = 10):
        self.q = q
        self.skip = skip
        self.limit = limit

async def dependency_model(item: Item, user: User | None = None):
    return {"item": item, "user": user if user else None}

#Sub dependencies
def dependency_query(q: str | None = None):
    return q

def dependency_query_or_cookie(
    q: Annotated[str | None, Depends(dependency_query)], 
    last_query: Annotated[str | None, Cookie()] = None
):
    print("Cookie value: ", last_query)
    if q:
        return q
    return ("Query not found, cookie value: " + last_query) if last_query else "No query or cookie found" #Both postman and swagger ui doesn't support cookie, so we can test it using browser dev panels.


@app.get("/")
def read_root():
    return {"Hello": "World!"}

#Dependency Injection
# common_annotation = Annotated[dependency_skip, Depends(dependency_skip)] 
common_annotation = Annotated[dependency_skip, Depends()] #FastAPI provides shortcut where dependency are specially a class, it will call to create an instance of the class
common_model_annotation = Annotated[dict, Depends(dependency_model)]

#Query parameters
@app.get("/items/", tags=["items"], deprecated=True)
def read_items(commons: common_annotation):
    return item_db[commons.skip: commons.skip + commons.limit]

@app.get("/users/", tags=["users"])
def read_users(commons: common_annotation):
    return user_db[commons.skip: commons.skip + commons.limit]

@app.get("/query/")
def read_query(query: Annotated[str, Depends(dependency_query_or_cookie)]):
    return {"q_or_cookie": query}


# @app.get("/items/{item_id}")
# async def read_item(item_id: int, q: str | None = None):
#     if item_id not in [item["item_id"] for item in item_db]:
#         print(item_id)
#         raise HTTPException(status_code=404, detail="Item not found")
#     if q:   
#         return {"item_id": item_id, "q": q}
#     return {"item": item_db[item_id - 1x]}

@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(request, exc):
    print(f"HTTP exception occurred at {request.url}: {exc.detail}")
    return await http_exception_handler(request, exc)

@app.exception_handler(RequestValidationError)
async def custom_validation_exception_handler(request, exc):
    print(f"Validation error at {request.url}: {exc.errors()}")
    return await request_validation_exception_handler(request, exc)

@app.get("/items/{item_id}", tags=["items"])
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
    user_id: int, item_id: int, q: str | None = None, short: bool = False
):
    item = {"item_id": item_id, "owner_id": user_id}    
    if q:
        item.update({"q": q})
    if not short:
        item.update(
            {"description": "This is an amazing item that has a long description"}
        )
    return item

@app.post("/items/", summary="Create an item", response_description="The created item", tags=["items"])
def create_item(common: common_model_annotation):
    '''
        Create an item with all the informations:
        - **name**: each item must have a name
        - **description**: a long description of the item 
        - **price**: required price of the item
        - **tax**: if the item doesn't have tax, you can skip this field
        - **tags**: a set of unique tag strings for the item
        - **image**: an optional image of the item, which should be a valid URL and a name for the image
    '''
    item_dict = common["item"].model_dump()
    if common["item"].tax:
        price_with_tax = common["item"].price + common["item"].tax
        item_dict.update({"price_with_tax": price_with_tax})
    return (item_dict, common["user"] if common["user"] else None)

# #Request body + path parameters
# @app.put("/items/{item_id}")
# def update_item(item_id: int, item: Item, q: str | None = None):
#     result = {"item_id": item_id, **item.model_dump()}#** is used to unpack the dictionary returned by model_dump() and merge it with the item_id key-value pair in the returned dictionary.
#     if q:
#         result.update({"q": q})
#     return result

#Multiple body parameters
@app.put("/items/{item_id}", tags=["items"])
def update_item(item_id: int, common: common_model_annotation):
    return {"item_id": item_id, "item": common["item"], "user": common["user"]}

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

