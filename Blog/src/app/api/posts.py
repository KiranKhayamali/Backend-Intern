from typing import Annotated, Any
from fastapi import APIRouter, Depends, Request
from fastcrud import PaginatedListResponse, compute_offset, paginated_response

from ..core.dependencies import SessionDep, get_current_active_user
from ..core.db.session import async_get_db
# from ..core.security import 
from ..core.exceptions.http_exceptions import NotFoundException
from ..schemas.post import PostRead, PostCreate, PostCreateInternal, PostUpdate
from ..repositories.post_repository import crud_posts




router = APIRouter(tags=["posts"], prefix="/posts")


@router.get("/", response_model=PaginatedListResponse[PostRead])
async def read_posts(request:Request, db: Annotated[SessionDep, Depends(async_get_db)], page: int = 1, items_per_page: int = 10) -> dict:
    posts_data = await crud_posts.get_multi(
        db=db,
        offset=compute_offset(page, items_per_page),
        limit=items_per_page,
        is_deleted=False
    )

    response: dict[str, Any] = paginated_response(crud_data=posts_data,page=page, items_per_page=items_per_page)
    return response

@router.post("/", response_model=PostRead, status_code=201)
async def create_post(request: Request, post: PostCreate, current_user: Annotated[SessionDep, Depends(get_current_active_user)], db: Annotated[SessionDep, Depends(async_get_db)]) -> dict[str, Any]:
    post_internal_dict = post.model_dump()
    post_internal_dict["author_id"] = current_user.id
    post_internal = PostCreateInternal(**post_internal_dict)
    created_post = await crud_posts.create(db=db, object=post_internal, schema_to_select=PostRead)

    if created_post is None:
        raise NotFoundException("Failed to create the post!!!")
    
    return created_post