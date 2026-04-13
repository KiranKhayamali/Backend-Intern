from __future__ import annotations
from typing import Annotated, TYPE_CHECKING
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, HTTPException, status


from .db.session import async_get_db
from ..repositories.user_repository import crud_users
from ..schemas.user import UserRead
from .security import oauth2_scheme


SessionDep = Annotated[AsyncSession, Depends(async_get_db)]


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], db: SessionDep):
    from .security import TokenType, oauth2_scheme, verify_token

    token_data = await verify_token(token, TokenType.ACCESS, db)
    if not token_data:
        return HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User not authenticated!!!")
    
    if "@" in token_data.username_or_email:
        user = await crud_users.get(db=db, email=token_data.username_or_email, is_deleted=False)
    else:
        user = await crud_users.get(db=db, username=token_data.username_or_email, is_deleted=False)

    if not user:
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found!!!")
    
    return user

async def get_current_active_user(current_user: Annotated[UserRead, Depends(get_current_user)]):
    if getattr(current_user, "disabled", False):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
    return current_user

