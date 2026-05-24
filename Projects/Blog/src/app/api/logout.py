from typing import Optional, Any
from fastapi import APIRouter, Cookie, Response

from ..core.exceptions.http_exceptions import UnauthorizedException
from ..core.db.redis_connect import redis_client

router = APIRouter(tags=["login"], prefix="/users/auth")


@router.post("/logout")
async def logout(
    response: Response,
    refresh_token: Optional[str] = Cookie(None, alias="refresh_token"),
) -> dict[str, Any]:
    try:
        if not refresh_token:
            raise UnauthorizedException("Refresh Token Not Found!!!")

        redis_client.delete(f"auth:refresh:{refresh_token}")
        response.delete_cookie(key="refresh_token")

        return {"message": "Logged Out Successfully!!!"}

    except Exception as exec:
        raise UnauthorizedException(f"Invalid Token!!! Details: {exec}")
