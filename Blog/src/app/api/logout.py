from typing import Optional, Annotated, Any
from fastapi import APIRouter, Cookie, Depends, Response
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.exceptions.http_exceptions import UnauthorizedException
from ..core.security import blacklist_tokens, oauth2_scheme
from ..core.db.session import async_get_db
from ..core.db.redis_connect import redis_client


router = APIRouter(tags=["login"], prefix="/users/auth")


@router.post("/logout")
async def logout(
    response: Response, 
    access_token: str = Depends(oauth2_scheme), 
    refresh_token: Optional[str] = Cookie(None, alias="refresh_token"), 
    db: AsyncSession = Depends(async_get_db)
) -> dict[str, Any]:
    try:
        if not refresh_token:
            raise UnauthorizedException("Refresh Token Not Found!!!")
        
        if access_token.startswith("Bearer "):
            access_token = access_token.split(" ")[1]
        
        await blacklist_tokens(access_token=access_token, db=db)

        redis_client.delete(f"auth:refresh:{refresh_token}")
        response.delete_cookie(key="refresh_token")

        return {"message": "Logged Out Successfully!!!"}
    
    except Exception as exec:
        raise UnauthorizedException(f"Invalid Token!!! Details: {exec}")


