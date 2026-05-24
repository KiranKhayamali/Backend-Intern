from fastcrud import FastCRUD

from ..models.token_blacklist import TokenBlacklist
from ..core.schemas import TokenBlacklistCreate, TokenBlacklistRead, TokenBlacklistUpdate

CRUDTokenBlacklist = FastCRUD[
    TokenBlacklist,
    TokenBlacklistCreate,
    TokenBlacklistRead,
    TokenBlacklistUpdate,
    TokenBlacklistUpdate,
    TokenBlacklistUpdate, # TokenBlacklistUpdate is duplicated because FastCRUD requires at least 6 arguments
]

crud_token_blacklist = CRUDTokenBlacklist(TokenBlacklist)