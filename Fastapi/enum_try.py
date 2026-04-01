from enum import Enum
from typing import Annotated 

from fastapi import FastAPI, File, Form, UploadFile


class ModelName(str, Enum):
    alexnet = "alexnet"
    resnet = "resnet"
    lenet = "lenet"


app = FastAPI()


# @app.get("/models/{model_name}")
# async def get_model(model_name: ModelName):
#     if model_name is ModelName.alexnet:
#         return {"model_name": model_name, "message": "Deep Learning FTW!"}

#     if model_name.value == "lenet":
#         return {"model_name": model_name, "message": "LeCNN all the images"}

#     return {"model_name": model_name, "message": "Have some residuals"}

# @app.get("/model/{model_path: path}") #Path parameters that contains another path,
# async def get_model_path(model_path: str):
#     return (f"Model path: {model_path}")

#Request Form and Files
@app.post("/files/")
async def create_file(
    file: Annotated[UploadFile, File(description= "File uploaded using UploadFIle")],
    fileb: Annotated[bytes, File(description="File uploaded as bytes")],
    token: Annotated[str, Form(description= "Token for authentication using Form")]):
    return {"file_size_upload": file.content_type, "file_size_bytes": len(fileb), "token": token}