from typing import Annotated, List
from fastapi import Depends, HTTPException, status, APIRouter, Response, Request
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta

from ..core.config import settings
from ..core.deps import SessionDep
from ..schemas.user import UserRead, UserCreate, UserUpdate
from ..schemas.token import Token
from ..core.utils.auth import authenticate_user, create_token, decode_token
from ..services.user_service import UserService
from ..repositories.user_repository import UserRepository
from ..dependencies.auth_dependency import get_current_user


router = APIRouter()


def get_user_service(db: SessionDep) -> UserService:
    return UserService(db)


@router.get("/me", response_model=UserRead, status_code=status.HTTP_200_OK)
async def read_users_me(user_service: UserService = Depends(get_user_service), user: UserRead = Depends(get_current_user)):
    return await user_service.get_user_by_username(user.username)


@router.get("/", response_model=List[UserRead], status_code=status.HTTP_200_OK)
async def read_users(user_service: UserService = Depends(get_user_service)):
    return await user_service.get_all_users()


@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_user(user:UserCreate, user_service: UserService = Depends(get_user_service)):
    return await user_service.create_user(user)


@router.put("/{user_id}", response_model=UserRead, status_code=status.HTTP_200_OK)
async def update_user(user_id: int, user_data: UserUpdate, user_service: UserService = Depends(get_user_service)):
    return await user_service.update_user(user_id, user_data)


@router.post("/token", response_model=Token, status_code=status.HTTP_200_OK)
async def login(response: Response, form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: SessionDep):
    repo = UserRepository(db)
    user = await authenticate_user(repo, form_data.username, form_data.password)

    acess_token_ttl = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_token_ttl = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

    access_token = create_token(data={"sub": user.username}, expires_delta=acess_token_ttl, token_type="access")
    refresh_token = create_token(data={"sub": user.username}, expires_delta=refresh_token_ttl, token_type="refresh")
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=False,  # Set to True in production with HTTPS
        samesite="lax",
        max_age=int(acess_token_ttl.total_seconds()),
        path="/"
        )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=int(refresh_token_ttl.total_seconds()),
        path="/"
        )
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.post("/refresh", response_model=Token, status_code=status.HTTP_200_OK)
async def refresh_token(request: Request, response: Response):
    current_refresh_token = request.cookies.get("refresh_token")
    if not current_refresh_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token missing")

    payload = await decode_token(current_refresh_token, expected_type="refresh")
    username = payload.get("sub")
    if not username:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    new_access_token = create_token(data={"sub": username}, expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES), token_type="access")
    response.set_cookie(
        key="newaccess_token",
        value=new_access_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=int(timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES).total_seconds()),
        path="/"
    )
    return {"access_token": new_access_token, "token_type": "bearer"}


@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(response: Response):
    response.delete_cookie(key="access_token", path="/")
    response.delete_cookie(key="refresh_token", path="/")
    return {"message": "Successfully logged out!"}