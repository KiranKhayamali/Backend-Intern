from __future__ import annotations
from typing import Annotated, TYPE_CHECKING
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, HTTPException, status, Request


from .db.session import async_get_db
from ..repositories.user_repository import crud_users
from ..schemas.user import UserRead
from .security import TokenType, oauth2_scheme, verify_token
from .logger import logging

SessionDep = Annotated[AsyncSession, Depends(async_get_db)]

logger = logging.getLogger(__name__)


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)], db: SessionDep
):
    token_data = await verify_token(token, TokenType.ACCESS, db)
    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="User not authenticated!!!"
        )

    if "@" in token_data.username_or_email:
        user = await crud_users.get(
            db=db, email=token_data.username_or_email, is_deleted=False
        )
    else:
        user = await crud_users.get(
            db=db, username=token_data.username_or_email, is_deleted=False
        )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found!!!"
        )

    return user


async def get_current_active_user(
    current_user: Annotated[UserRead, Depends(get_current_user)],
):
    if getattr(current_user, "disabled", False):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
        )
    return current_user


async def get_optional_user(request: Request, db: SessionDep) -> dict | None:
    token = request.headers.get("Authorization")
    if not token:
        return None

    try:
        token_type, _, token_value = token.partition(" ")
        if token_type.lower() != "bearer" or not token_value:
            return None

        token_data = await verify_token(token_value, TokenType.ACCESS, db)
        if token_data is None:
            return None

        return await get_current_user(token_value, db=db)

    except HTTPException as http_exec:
        if http_exec.status_code != 401:
            logger.error(
                f"Unexpected HTTPExection in get_optional_user: {http_exec.detail}"
            )
        return None

    except Exception as exec:
        logger.error(f"Unexpected error in get_optional_user: {exec}")
        return None
