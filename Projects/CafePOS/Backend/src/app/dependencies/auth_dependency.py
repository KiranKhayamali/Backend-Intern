from typing import Annotated
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

from ..core.utils.security import decode_token
from ..core.db.session import SessionDep
from ..services.user_service import UserService
from ..repositories.user_repository import UserRepository
from ..core.exceptions.http_exceptions import UnauthorizedException, NotFoundException
from types import SimpleNamespace
from ..schemas.user import UserRead


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], db: SessionDep) -> UserRead:
    payload = await decode_token(token)
    user_contact_number: str = payload.get("sub")
    if user_contact_number is None:
        raise UnauthorizedException(detail="Invalid token payload!")

    user_service = UserService(UserRepository(db))
    user = await user_service.get_user_by_contact_number(user_contact_number)
    if not user:
        raise NotFoundException(detail="User not Found!")

    # Normalize user to an attribute-accessible object in case a dict is returned
    if isinstance(user, dict):
        user = SimpleNamespace(**user)

    return user
