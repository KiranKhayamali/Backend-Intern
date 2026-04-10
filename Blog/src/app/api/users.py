from typing import Annotated, Any
from fastapi import APIRouter, Depends, Request
from fastcrud import PaginatedListResponse, compute_offset, paginated_response

from ..core.dependencies import SessionDep
from ..core.db.session import async_get_db
from ..core.security import get_password_hash
from ..core.exceptions.http_exceptions import DuplicateValueException, ForbiddenException, NotFoundException
from ..schemas.user import UserRead, UserCreate, UserCreateInternal, UserUpdate
from ..repositories.user_repository import crud_users


router = APIRouter(tags=["users"], prefix="/users")


@router.get("/", response_model=PaginatedListResponse[UserRead])
async def read_users(request: Request, db: Annotated[SessionDep, Depends(async_get_db)], page: int = 1, items_per_page: int = 10) -> dict:
    users_data = await crud_users.get_multi(
        db=db,
        offset=compute_offset(page, items_per_page),
        limit=items_per_page,
        is_deleted=False
    )

    response: dict[str, Any] = paginated_response(crud_data=users_data, page=page, items_per_page=items_per_page)
    return response

@router.post("/", response_model=UserRead, status_code=201)
async def create_user(request: Request, user: UserCreate, db: Annotated[SessionDep, Depends(async_get_db)]) -> dict[str, Any]:
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