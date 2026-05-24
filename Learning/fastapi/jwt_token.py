#https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/#handle-jwt-tokens for the reference of jwt token implementation in FastAPI.

from typing import Annotated
from datetime import datetime, timedelta, timezone

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel

import jwt
from jwt.exceptions import InvalidTokenError
from pwdlib import PasswordHash

SECRET_KEY = "fdd7e5438a8a1a5765d10a466f45ca7aaec8fb3896ef2d000ee9df8faeede9a4" #use openssl rand -hex 32 to generate a random secret key
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

password_hash = PasswordHash.recommended()

user_db = {
    "kiran": {
        "username": "kiran",
        "fullname": "Kiran Khayamali",
        "email": "kiran@example.com",
        "hashed_password": password_hash.hash("secret1"),
        "disabled": False 
    },
    "ashura": {
        "username": "ashura",
        "fullname": "Unknown Ashura",
        "email": "ashura@example.com",
        "hashed_password": password_hash.hash("secret2"),
        "disabled": False 
    }
}

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None

class User(BaseModel):
    username: str
    email: str | None = None
    fullname: str | None = None 
    disabled: bool | None = None 

class UserInDB(User):
    hashed_password: str


DUMMY_HASH = password_hash.hash("dummypassword")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI()

def verify_password(plain_password, hashed_password):
    return password_hash.verify(plain_password, hashed_password)

def get_password_hash(password):
    return password_hash.hash(password)

def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)
    
def authenticate_user(db, username: str, password: str):
    user = get_user(db, username)
    if not user: 
        verify_password(password, DUMMY_HASH) #to prevent timing attack, we will verify the password with a dummy hash if the user is not found in the database. This will take the same amount of time as verifying the password for a valid user, so it will prevent attackers from being able to determine if a username is valid or not based on the response time.
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except InvalidTokenError:
        raise credentials_exception
    user = get_user(user_db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(current_user: Annotated[User, Depends(get_current_user)]):
    if current_user.disabled:
        raise HTTPException(status_code=status  .HTTP_400_BAD_REQUEST, detail="Inactive user")
    return current_user

@app.post("/token")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> Token:
    user = authenticate_user(user_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect username or password")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me")
async def read_users_me(current_user: Annotated[User, Depends(get_current_active_user)]) -> User:
    return current_user







