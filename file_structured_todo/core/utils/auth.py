from datetime import datetime, timedelta, timezone
from pwdlib import PasswordHash
from pwdlib.exceptions import UnknownHashError
from typing import Protocol
from fastapi import HTTPException, status

from jose import jwt, JWTError

from ..config import settings
from ...schemas.user import UserRead

password_hash = PasswordHash.recommended()


class UserUtils(Protocol):
    async def get_user_by_username(self, username: str) -> UserRead | None:
        ...


def verify_password(plain_password, hashed_password) -> bool:
    try:
        return password_hash.verify(plain_password, hashed_password)
    except UnknownHashError:
        return False


def get_password_hash(password) -> str:
    return password_hash.hash(password)


def create_token(data: dict, expires_delta: timedelta | None = None, token_type: str = "access") -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire, "type": token_type})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


async def authenticate_user(repo: UserUtils, username:str, password: str) -> UserRead | str  :
    user = await repo.get_user_by_username(username)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User Not Found")

    if not verify_password(password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


async def decode_token(token: str, expected_type: str = "access") -> dict:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate the refresh token!!!",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        token_type = payload.get("type")
        if token_type != expected_type:
            raise credentials_exception
        sub: str = payload.get("sub")
        if sub is None:
            raise credentials_exception
        return payload
    except JWTError:
        raise credentials_exception
