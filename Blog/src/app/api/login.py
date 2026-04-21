from typing import Annotated
from datetime import UTC, datetime, timedelta
import secrets

from fastapi import APIRouter, Depends, Request, Response
from fastapi.security import OAuth2PasswordRequestForm

from ..core.dependencies import SessionDep
from ..core.config import settings
from ..core.db.redis_connect import redis_client
from ..core.exceptions.http_exceptions import UnauthorizedException
from ..core.schemas import Token
from ..core.security import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    authenticate_user,
    create_access_token,
)

router = APIRouter(tags=["login"], prefix="/users/auth")


@router.post("/login", response_model=Token)
async def login_for_access_token(
    response: Response,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: SessionDep,
):
    user = await authenticate_user(
        username_or_email=form_data.username, password=form_data.password, db=db
    )
    if not user:
        raise UnauthorizedException("Wrong Username, Wrong Password!!!")

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = await create_access_token(
        data={"sub": user["username"]}, expires_delta=access_token_expires
    )

    # Created Refresh Token using Redis to store the refresh tokens
    refresh_token = secrets.token_urlsafe(32)
    refresh_key = f"auth:refresh:{refresh_token}"
    redis_client.hset(
        refresh_key,
        mapping={
            "username": user["username"],
            "expires_at": (
                datetime.now(UTC) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
            ).isoformat(),
        },
    )

    redis_client.expire(refresh_key, settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60)

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=False,  # True in production with HTTPS
        samesite="lax",
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
    )

    return {"access_token": access_token, "token_type": "bearer"}


# Refresh Token using Redis to store the refresh tokens
@router.post("/refresh")
async def refresh_access_token(request: Request) -> dict[str, str]:
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise UnauthorizedException("Refresh Token misssing!!!")

    refresh_key = f"auth:refresh:{refresh_token}"
    user_data = redis_client.hgetall(refresh_key)
    if not user_data:
        raise UnauthorizedException("Invalid Refresh Token!!!")

    username = user_data.get("username")
    if not username:
        raise UnauthorizedException("Corrupted Refresh Token data!!!")

    new_access_token = await create_access_token(data={"sub": username})
    return {"new_access_token": new_access_token, "token_type": "bearer"}
