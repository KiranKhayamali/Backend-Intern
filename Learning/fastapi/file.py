from fastapi import FastAPI, File, UploadFile
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

import os
import shutil

app = FastAPI() 

#Basic File upload 
@app.post("/upload/", tags=["File"])
async def upload_file(file: bytes = File("testFile.txt")):
    return {f"File size: {len(file)}"}

#UploadFile 
@app.post("/uploadFile/", tags=["UploadFile"])
async def upload_file(file: UploadFile = File("testFile.txt")):
    return {
        "filename": file.filename,
        "Content Type": file.content_type
    }

#Checking File Types
@app.post("/upload-check-mime/")
async def upload_file(file: UploadFile = File("testFile.txt")):
    if file.content_type not in ['image/jpeg', 'image/png']:
        return {"error": "Invalid file type"}
    
    return {"message": "Valid file type"}

@app.post("/upload-check-extension/")
async def upload_file(file: UploadFile = File("testFile.txt")):
    ext = os.path.split(file.filename)[1]

    if ext not in [".jpg", "png"]:
        return {"error": "Invalid Extension"}
    
    return {"message": "Valid Extension"}

#Saving files(making them static)
@app.post("/upload-save/")
async def upload_file(file: UploadFile = File("testFile.txt")):
    file_path = f"uploads/{file.filename}"

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {
        "url": f"/static/{file.filename}"
    }
    
#Making files statically available 
app.mount("/static", StaticFiles(directory="uploads"), name="static")

#Download Files
@app.get("/download/{filename}")
async def download_file(filename: str):
    file_path = f"uploads/{filename}"
    return FileResponse(path=file_path, filename=filename)