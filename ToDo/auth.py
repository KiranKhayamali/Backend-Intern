from typing import Annotated
from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from .models import User
from pwdlib import PasswordHash
from pwdlib.exceptions import UnknownHashError
from sqlalchemy import select


import jwt 
from jwt.exceptions import InvalidTokenError
from .deps import SessionDep

SECRET_KEY = "5951cd724eb131212fc22c003f138c65c833c862e0d22719f6a897ec05fe9a44"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/token")

pasword_hash = PasswordHash.recommended()

DUMMY_HASH = pasword_hash.hash("dummypassword")

def verify_password(plain_password, hashed_password):
    try:
        return pasword_hash.verify(plain_password, hashed_password)
    except UnknownHashError:
        return False

def get_password_hash(password):
    return pasword_hash.hash(password)

async def authenticate_user(db:SessionDep, username:str, password: str):
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()
    if not user:
        verify_password(password, DUMMY_HASH)
        return False

    if verify_password(password, user.password):
        return user

    # Backward compatibility for users created before password hashing was added.
    if user.password == password:
        user.password = get_password_hash(password)
        await db.commit()
        await db.refresh(user)
        return user

    return False


def create_access_token(data: dict, expires_delta: timezone| None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], db: SessionDep):
    from .models import User
    from .deps import get_db
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate user's credentials!!!",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id_raw = payload.get("sub")
        if user_id_raw is None:
            raise credentials_exception
        user_id = int(user_id_raw)
    except (InvalidTokenError, ValueError, TypeError):
        raise credentials_exception
    
    user = await db.get(User, user_id)

    if not user:
        raise credentials_exception

    return user
    
async def get_current_active_user(current_user: Annotated[User, Depends(get_current_user)]):
    if getattr(current_user, "disabled", False):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
    return current_user