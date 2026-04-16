from typing import Annotated, Any
from fastapi import APIRouter, Depends, Request
from fastcrud import PaginatedListResponse, compute_offset, paginated_response
from datetime import datetime, UTC

from ..core.dependencies import SessionDep
from ..core.db.session import async_get_db
from ..core.security import get_password_hash, blacklist_token, oauth2_scheme
from ..core.exceptions.http_exceptions import DuplicateValueException, ForbiddenException, NotFoundException
from ..schemas.user import UserRead, UserCreate, UserCreateInternal, UserUpdate, UserUpdateInternal, UserDelete, UserRestoreDelete
from ..repositories.user_repository import crud_users
from ..core.dependencies import get_current_active_user


router = APIRouter(tags=["users"], prefix="/users")


@router.get("/", response_model=PaginatedListResponse[UserRead])
async def read_users(request: Request, db: SessionDep, page: int = 1, items_per_page: int = 10) -> dict:
    users_data = await crud_users.get_multi(
        db=db,
        offset=compute_offset(page, items_per_page),
        limit=items_per_page,
        is_deleted=False
    )

    response: dict[str, Any] = paginated_response(crud_data=users_data, page=page, items_per_page=items_per_page)
    return response

@router.get("/me", response_model=UserRead)
async def read_current_user(current_user: Annotated[UserRead, Depends(get_current_active_user)]):
    return current_user

@router.get("/{username_or_email}", response_model=UserRead)
async def read_user(username_or_email:str, db:SessionDep) -> dict[str, Any]:
    if "@" in username_or_email:
        db_user = await crud_users.get(db=db, email=username_or_email, is_deleted=False, schema_to_select=UserRead)
    else:
        db_user = await crud_users.get(db=db, username=username_or_email, is_deleted=False, schema_to_select=UserRead)

    if not db_user:
        raise NotFoundException("User Not Found!!!")
    
    return db_user

@router.post("/", response_model=UserRead, status_code=201)
async def create_user(request: Request, user: UserCreate, db: SessionDep) -> dict[str, Any]:
    email_row = await crud_users.exists(db=db, email=user.email)
    if email_row:
        raise DuplicateValueException("Email is already registered!!!")
    
    username_row = await crud_users.exists(db=db, username=user.username)
    if username_row:
        raise DuplicateValueException("Username not available!!!")

    
    user_internal_dict = user.model_dump()
    user_internal_dict.pop("posts", None)
    user_internal_dict["hashed_password"] = get_password_hash(password=user_internal_dict["password"])
    del user_internal_dict["password"]

    user_internal = UserCreateInternal(**user_internal_dict)
    created_user = await crud_users.create(db=db, object=user_internal, schema_to_select=UserRead)

    if created_user is None:
        raise NotFoundException("Failed to create the user!!!")
    
    return created_user

@router.put("/{username_or_email}", response_model=UserRead)
async def update_user(username_or_email:str, user_update: UserUpdate, current_user: Annotated[UserRead, Depends(get_current_active_user)], db: SessionDep) -> dict[str, Any]:
    if "@" in username_or_email:
        db_user = await crud_users.get(db=db, email=username_or_email, is_deleted=False, schema_to_select=UserRead)
    else:
        db_user = await crud_users.get(db=db, username=username_or_email, is_deleted=False, schema_to_select=UserRead)
    
    if not db_user:
        raise NotFoundException("User Not Found!!!")

    if current_user["id"] != db_user["id"]:
        raise ForbiddenException()
    
    user_update_dict = user_update.model_dump(exclude_unset=True)
    if "password" in user_update_dict:
        user_update_dict["hashed_password"] = get_password_hash(password=user_update_dict["password"])
        del user_update_dict["password"]
    
    user_update_dict["updated_at"] = datetime.now(UTC)
    user_update_internal_dict = UserUpdateInternal(**user_update_dict).model_dump(exclude_unset=True)

    updated_user = await crud_users.update(
        db=db,
        object=user_update_internal_dict,
        schema_to_select=UserRead,
        return_as_model=True,
        id=db_user["id"],
    )

    if updated_user is None:
        raise NotFoundException("Failed to update user!!!")

    return updated_user


@router.delete("/{username_or_email}", status_code=204)
async def delete_user(username_or_email:str, current_user: Annotated[UserRead, Depends(get_current_active_user)], db: SessionDep, token:str = Depends(oauth2_scheme)):
    if "@" in username_or_email:
        db_user = await crud_users.get(db=db, email=username_or_email, is_deleted=False, schema_to_select=UserRead)
    else:
        db_user = await crud_users.get(db=db, username=username_or_email,
        is_deleted=False, schema_to_select=UserRead)
    
    if not db_user:
        raise NotFoundException("User Not Found !!!")
        
    if current_user["id"] != db_user["id"]:
        raise ForbiddenException()
    
    await crud_users.delete(db=db, id=db_user["id"])
    await blacklist_token(token=token, db=db)
    return {"message": f"{current_user["username"]} has been deleted successfully!!!"}