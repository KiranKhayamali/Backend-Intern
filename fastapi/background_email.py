from typing import Annotated
from fastapi import FastAPI, BackgroundTasks, Depends

app = FastAPI()

def write_log(message:str):
    with open("log.txt", mode="w") as log:
        log.write(message)

def get_query(background_task:BackgroundTasks, q:str | None = None):
    if q:
        message = f"Found Query: {q}\n"
        background_task.add_task(write_log, message)
    return q

def write_notification(email:str, message=""):
    with open("log.txt", mode="w") as email_file:
        content = f"Notification for {email}: {message}"
        email_file.write(content)

# @app.post("/send-notification/{email}")
# def send_notification(email:str, background_tasks:BackgroundTasks):
#     background_tasks.add_task(write_notification, email, message="Some notification")
#     return {"message": "Notification sent using the background tasks"}

@app.post("/send-notification/{email}")
def send_notification(email:str, background_tasks:BackgroundTasks, q: Annotated[str, Depends(get_query)]):
    message = f"'{q}' message sent to {email}\n"
    background_tasks.add_task(write_log, message)
    return {"message": "Message sent in email"}

# def read_notification(email:str, message:""):

