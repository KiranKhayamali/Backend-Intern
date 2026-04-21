from __future__ import annotations
from datetime import datetime, timedelta, timezone
from fastapi.security import OAuth2PasswordBearer
from pwdlib import PasswordHash
from pydantic import SecretStr
from enum import Enum
from typing import TYPE_CHECKING

from jose import jwt, JWTError
from .config import settings
from .schemas import TokenData
from ..repositories.user_repository import crud_users
from ..repositories.token_blacklist_repository import crud_token_blacklist
from ..repositories.token_blacklist_repository import TokenBlacklistCreate
from ..core.exceptions.http_exceptions import CustomException



if TYPE_CHECKING:
    from .dependencies import SessionDep

SECRET_KEY: SecretStr = settings.SECRET_KEY
ALGORITHM: str = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES: int = settings.ACCESS_TOKEN_EXPIRE_MINUTES
REFRESH_TOKEN_EXPIRE_DAYS: int = settings.REFRESH_TOKEN_EXPIRE_DAYS


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/auth/login")

passwword_hash = PasswordHash.recommended()


class TokenType(str, Enum):
    ACCESS = "access"
    REFRESH = "refresh"


async def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        checker: bool = passwword_hash.verify(plain_password, hashed_password)
        return checker
    except Exception:
        return False
    
def get_password_hash(password: str) -> str:
    hashed_password: str = passwword_hash.hash(password)
    return hashed_password

async def authenticate_user(db: SessionDep, username_or_email: str, password: str):
    if "@" in username_or_email:
        db_user = await crud_users.get(db=db, email=username_or_email, is_deleted=False)
    else:
        db_user = await crud_users.get(db=db, username=username_or_email, is_deleted=False)

    if not db_user:
        return False

    password_valid = await verify_password(password, db_user["hashed_password"])
    if not password_valid:
        return False
    
    return db_user


async def create_access_token(data: dict, expires_delta: timedelta | None = None)-> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "token_type": TokenType.ACCESS})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY.get_secret_value(), algorithm=ALGORITHM)
    return encoded_jwt


async def create_refresh_token(data:dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "token_type": TokenType.REFRESH})
    enocoded_jwt = jwt.encode(to_encode, SECRET_KEY.get_secret_value(), algorithm=ALGORITHM)
    return enocoded_jwt


async def verify_token(token:str, expected_token_type: TokenType, db:SessionDep) -> TokenData | None:
    is_blacklisted = await crud_token_blacklist.exists(db, token=token)
    if is_blacklisted:
        raise CustomException(401, "Token has been blacklisted!, Please login with another token. ")
    
    try:
        payload = jwt.decode(token, SECRET_KEY.get_secret_value(), algorithms=[ALGORITHM]) 
        username_or_email:str | None = payload.get("sub")
        token_type:str | None= payload.get("token_type")

        if username_or_email is None or token_type != expected_token_type.value:
            return None
        
        return TokenData(username_or_email=username_or_email)
    
    except JWTError:
        return None
    

async def blacklist_tokens(access_token:str, db: SessionDep) -> None:
    if not access_token or access_token.count(".") != 2:
        raise ValueError("Invalid JWT format")

    payload = jwt.decode(access_token, SECRET_KEY.get_secret_value(), algorithms=[ALGORITHM])
    exp_timestamp = payload.get("exp")
    if exp_timestamp is not None:
        expires_at = datetime.fromtimestamp(exp_timestamp)
        await crud_token_blacklist.create(db, object=TokenBlacklistCreate(token=access_token, expires_at=expires_at))


async def blacklist_token(token:str, db: SessionDep) -> None:
    payload = jwt.decode(token, SECRET_KEY.get_secret_value(), algorithms=[ALGORITHM])
    exp_timestamp = payload.get("exp")
    if exp_timestamp is not None:
        expires_at = datetime.fromtimestamp(exp_timestamp)
        await crud_token_blacklist.create(db, object=TokenBlacklistCreate(token=token, expires_at=expires_at))


