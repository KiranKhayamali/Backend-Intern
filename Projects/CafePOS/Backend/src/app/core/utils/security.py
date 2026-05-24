from typing import Protocol
from pwdlib import PasswordHash
from jose import jwt, JWTError
from datetime import datetime, timedelta

from ..config import settings
from ...schemas.user import UserRead
from ..exceptions.http_exceptions import UnauthorizedException, NotFoundException

password_hash = PasswordHash.recommended()


class SecurityUtils(Protocol):
    async def get_user_by_contact_number(self, contact_number: str) -> UserRead | None:
        ...


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_hash.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return password_hash.hash(password)


async def authenticate_user(repo: SecurityUtils, contact_number: str, password: str) -> UserRead:
    user = await repo.get_user_by_contact_number(contact_number)
    if not user:
        raise NotFoundException(detail="User not found!")

    if not verify_password(password, user.hashed_password):
        raise UnauthorizedException(detail="Incorrect password!")

    return user


def create_token(data: dict, expire_delta: timedelta | None = None, token_type: str = "access") -> str:
    to_encode = data.copy()
    if expire_delta:
        expire = datetime.now() + expire_delta
    else:
        expire = datetime.now() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire, "type": token_type})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


async def decode_token(token:str, expected_type: str = "access") -> dict:
    credentials_exception = UnauthorizedException(detail="Could not validate credentials!")

    try:
        payload = jwt.decode(token=token, key=settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        if payload.get("type") != expected_type:
            raise credentials_exception

        subject: str = payload.get("sub")
        if subject is None:
            raise credentials_exception

        return payload
    except JWTError:
        raise credentials_exception
