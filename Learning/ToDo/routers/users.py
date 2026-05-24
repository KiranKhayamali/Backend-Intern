from typing import Annotated, List
from fastapi import Depends, Query, HTTPException, status, APIRouter
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from fastapi.security import OAuth2PasswordRequestForm
from ..auth import ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token, get_current_active_user, authenticate_user, get_password_hash
from datetime import timedelta

from ..models import User, UserSchema
from ..deps import SessionDep



router = APIRouter()


@router.post("/token")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: SessionDep):
    user = await authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect username or password")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": str(user.id)}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me")
async def read_users_me(current_user: Annotated[User, Depends(get_current_active_user)]):
    return current_user

@router.get("/", response_model=List[UserSchema])
async def read_users(db:SessionDep, offset:int = 0, limit: Annotated[int, Query(le=5)] = 5):
    select_sql = select(User).options(selectinload(User.notes)).offset(offset).limit(limit)
    result = await db.execute(select_sql)
    users = result.scalars().all()
    if not users:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User Not Found")
    return users


@router.post("/")
async def create_user(user:UserSchema, db:SessionDep):
    user_data = user.model_dump()
    user_data["password"] = get_password_hash(user.password)
    db_user = User(**user_data)
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user
