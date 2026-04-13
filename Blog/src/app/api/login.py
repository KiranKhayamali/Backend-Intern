from typing import Annotated
from datetime import datetime, timedelta 

from fastapi import APIRouter, Depends, Request, Response
from fastapi.security import OAuth2PasswordRequestForm

from ..core.dependencies import SessionDep
from ..core.config import settings
from ..core.db.session import async_get_db
from ..core.exceptions.http_exceptions import UnauthorizedException
from ..core.schemas import Token
from ..core.security import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    TokenType,
    authenticate_user,
    create_access_token,
    create_refresh_token,
    verify_token
)


router = APIRouter(tags=["login"], prefix="/users")


@router.post("/login", response_model=Token)
async def login_for_access_token(
    response: Response,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: SessionDep
):
    user = await authenticate_user(username_or_email=form_data.username, password=form_data.password, db=db)
    if not user:
        raise UnauthorizedException("Wrong Username, Wrong Password!!!")
    
    access_token_expires =  timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = await create_access_token(data={"sub": user["username"]},expires_delta=access_token_expires)

    refresh_token = await create_refresh_token(data={"sub": user["username"]})
    max_age = settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60

    response.set_cookie(
        key="refresh_token", value=refresh_token, httponly=True, secure=True, samesite="lax", max_age=max_age
    )

    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/refresh")
async def refresh_access_token(request:Request, db: SessionDep) -> dict[str, str]:
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise UnauthorizedException("Refresh Token misssing!!!")
    
    user_data = await verify_token(refresh_token, TokenType.REFRESH, db)
    if not user_data:
        raise UnauthorizedException("Invalid Refresh Token!!!")
    
    new_access_token = await create_access_token(data={"sub": user_data.username_or_email})
    return {"access_token_from_refresh_token": new_access_token, "token_type": "bearer"}