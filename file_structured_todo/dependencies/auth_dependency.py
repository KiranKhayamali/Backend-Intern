from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from ..core.utils.auth import decode_token
from ..core.deps import SessionDep
from ..services.user_service import UserService


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/token")


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], db: SessionDep) -> object:
    payload = await decode_token(token, "access")
    username = payload.get("sub")
    if not username:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")

    service = UserService(db)
    user = await service.get_user_by_username(username)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return user
