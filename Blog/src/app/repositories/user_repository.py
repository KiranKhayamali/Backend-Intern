from fastcrud import FastCRUD
from ..models.users import User
from ..schemas.user import  UserCreateInternal, UserRead, UserUpdate, UserUpdateInternal, UserDelete

CRUDUser = FastCRUD[User, UserCreateInternal, UserRead, UserUpdate, UserUpdateInternal, UserDelete]
crud_users = CRUDUser(User)