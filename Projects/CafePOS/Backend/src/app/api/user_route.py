from fastapi import APIRouter, Depends, status, Response, Request
from typing import List
from uuid import UUID
from datetime import timedelta, datetime
from typing import Annotated
from fastapi.security import OAuth2PasswordRequestForm

from ..core.db.session import SessionDep
from ..services.user_service import UserService
from ..repositories.user_repository import UserRepository
from ..schemas.user import UserRead, UserCreate, UserUpdate
from ..core.schemas import Token
from ..core.utils.security import authenticate_user, create_token, decode_token
from ..dependencies.auth_dependency import get_current_user
from ..core.config import settings
from ..core.exceptions.http_exceptions import UnauthorizedException, ForbiddenException

user_router = APIRouter(prefix="/users", tags=["users"])


def get_user_service(db: SessionDep) -> UserService:
    return UserService(repo=UserRepository(db=db))


@user_router.post("/login", response_model=dict, status_code=status.HTTP_200_OK)
async def login(response: Response, form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: SessionDep):
    repo = UserRepository(db=db)
    user = await authenticate_user(repo, form_data.username, form_data.password)

    access_token_ttl = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_token_ttl = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

    access_token = create_token(data={"sub": str(user.contact_number)}, expire_delta=access_token_ttl, token_type="access")
    refresh_token = create_token(data={"sub": str(user.contact_number)}, expire_delta=refresh_token_ttl, token_type="refresh")

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=int(access_token_ttl.total_seconds()),
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


@user_router.post("/refresh", response_model=Token, status_code=status.HTTP_200_OK)
async def refresh_token(request: Request, response: Response):
    current_refresh_token = request.cookies.get("refresh_token")
    if not current_refresh_token:
        raise UnauthorizedException(detail="Refresh token missing!")

    payload = await decode_token(current_refresh_token, expected_type="refresh")
    contact_number = payload.get("sub")
    if not contact_number:
        raise UnauthorizedException(detail="Invalid refresh token!")

    new_access_token_ttl = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    new_access_token = create_token(data={"sub": contact_number}, expire_delta=new_access_token_ttl, token_type="access")
    response.set_cookie(
        key="access_token",
        value=new_access_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=int(timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES).total_seconds()),
        path="/"
    )
    return {"access_token": new_access_token, "token_type": "bearer", "expire_at": (datetime.now() + new_access_token_ttl).isoformat()}


@user_router.post("/logout", response_model=dict, status_code=status.HTTP_200_OK)
async def logout(response: Response):
    response.delete_cookie(key="access_token", path="/")
    response.delete_cookie(key="refresh_token", path="/")
    return {"Message": "Successfully Logged out!"}



@user_router.get("/", response_model=List[UserRead], status_code=status.HTTP_200_OK)
async def read_all_users(user_service: UserService=Depends(get_user_service)):
    return await user_service.get_all_users()


@user_router.get("/me", response_model=UserRead, status_code=status.HTTP_200_OK)
async def read_current_user(user_service: UserService=Depends(get_user_service), current_user: UserRead=Depends(get_current_user)):
    return await user_service.get_user_by_contact_number(current_user.contact_number)


@user_router.get("/{user_id}", response_model=UserRead, status_code=status.HTTP_200_OK)
async def read_user(user_id: UUID, user_service: UserService=Depends(get_user_service)):
    return await user_service.get_user_by_id(user_id)


@user_router.get("/contacts/{contact_number}", response_model=UserRead, status_code=status.HTTP_200_OK)
async def read_user_by_contact_number(contact_number: str, user_service: UserService=Depends(get_user_service)):
    return await user_service.get_user_by_contact_number(contact_number)


@user_router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_user(user_create: UserCreate, user_service: UserService=Depends(get_user_service), current_user: UserRead=Depends(get_current_user)):
    if not current_user.is_admin:
        raise ForbiddenException(detail="Only admin users can create new users!")

    return await user_service.create_user(user_create)


@user_router.patch("/{user_id}", response_model=UserRead, status_code=status.HTTP_200_OK)
async def update_user(user_id: UUID, user_update: UserUpdate, user_service: UserService=Depends(get_user_service), current_user: UserRead=Depends(get_current_user)):
    if user_id != current_user.id and not current_user.is_admin:
        raise ForbiddenException(detail="You can only update your own profile!")

    return await user_service.update_user(user_id, user_update)


@user_router.delete("/{user_id}", response_model=dict, status_code=status.HTTP_200_OK)
async def delete_user(user_id: UUID, user_service: UserService=Depends(get_user_service), current_user: UserRead=Depends(get_current_user)):
    if user_id != current_user.id and not current_user.is_admin:
        raise ForbiddenException(detail="You can only delete your own profile!")

    return await user_service.delete_user(user_id)
