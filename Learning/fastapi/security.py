from typing import Annotated

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel

user_db = {
    "kiran": {
        "username": "kiran",
        "fullname": "Kiran Khayamali",
        "email": "kiran@example.com",
        "hashed_password": "fakehashedsecret1",
        "disabled": False 
    },
    "ashura": {
        "username": "ashura",
        "fullname": "Unknown Ashura",
        "email": "ashura@example.com",
        "hashed_password": "fakehashedsecret2",
        "disabled": False 
    }
}

app = FastAPI()

def hash_password(password: str):
    return "fakehashed" + password 

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class User(BaseModel):
    username: str
    email: str | None = None
    fullname: str | None = None 
    disabled: bool | None = None 

class UserInDB(User):
    hashed_password: str

def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)

def decode_token(token):
    user = get_user(user_db, token)
    return user

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    user = decode_token(token)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication credentials", headers={"WWW-Authenticate": "Bearer"})
    return user 

async def get_current_active_user(current_user: Annotated[User, Depends(get_current_user)]):
    if current_user.disabled:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
    return current_user

@app.post("/token")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user_dict = user_db.get(form_data.username)
    if not user_dict:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect username or password")
    user = UserInDB(**user_dict)
    hashed_password = hash_password(form_data.password)
    if not hashed_password == user.hashed_password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect username or password")
    
    return {"access_token": user.username, "token_type": "bearer"}

@app.get("/users/me")
async def read_users_me(current_user: Annotated[User, Depends(get_current_active_user)]):
    return current_user
