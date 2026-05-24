from typing import Annotated, Any
from fastapi import APIRouter, Depends
from fastcrud import PaginatedListResponse, compute_offset, paginated_response
from sqlalchemy import update
from datetime import datetime, UTC

from ..core.dependencies import SessionDep, get_current_active_user
from ..core.exceptions.http_exceptions import NotFoundException, ForbiddenException
from ..schemas.post import PostRead, PostCreate, PostCreateInternal, PostUpdate, PostUpdateInternal, PostReadWithComments
from ..repositories.post_repository import crud_posts
from ..repositories.user_repository import crud_users
from ..repositories.comment_repository import crud_comments
from ..schemas.user import UserRead
from ..models.posts import Post


router = APIRouter(tags=["posts"])


@router.get("/posts", response_model=PaginatedListResponse[PostRead])
async def read_posts(
    db: SessionDep, 
    page: int = 1, 
    items_per_page: int = 10
) -> dict:
    posts_data = await crud_posts.get_multi(
        db=db,
        offset=compute_offset(page, items_per_page),
        limit=items_per_page,
        is_deleted=False
    )

    response: dict[str, Any] = paginated_response(
        crud_data=posts_data,
        page=page, 
        items_per_page=items_per_page
    )
    return response

@router.get("/post/{post_id}", response_model=PostReadWithComments)
async def read_post(
    post_id: int, 
    db: SessionDep
) -> dict[str, Any]:
    db_post = await crud_posts.get(
        db=db, 
        id=post_id, 
        is_deleted=False, 
        schema_to_select=PostReadWithComments
    )
    if not db_post:
        raise NotFoundException("Post Not Found!!!")
    
    comments = await crud_comments.get_multi(
        db=db, 
        post_id=post_id
    )
    
    db_post["comments"] = comments["data"] or []
    
    await db.execute(
        update(Post)
        .where(Post.id == post_id)
        .values(
            number_of_comments=len(db_post["comments"]),
            view_count=Post.view_count + 1
        )
    )
    await db.commit()

    return db_post

@router.get("/posts/{username}", response_model=PaginatedListResponse[PostRead])
async def read_post_of_user(
    username: str, 
    db:SessionDep, 
    page: int = 1, 
    limit: int = 10
) -> dict[str, Any]:
    db_user = await crud_users.get(
        db=db, 
        username=username, 
        is_deleted=False, 
        schema_to_select=UserRead
    )
    if not db_user:
        raise NotFoundException("User Not Found!!!")
    
    posts_data = await crud_posts.get_multi(db=db, author_id=db_user["id"], is_deleted=False, offset=compute_offset(page, limit), limit=limit)
    result: dict[str, Any] = paginated_response(crud_data=posts_data, page=page, items_per_page=limit)
    return result


@router.post("/posts", response_model=PostRead, status_code=201)
async def create_post(post: PostCreate, current_user: Annotated[SessionDep, Depends(get_current_active_user)], db: SessionDep) -> dict[str, Any]:
    db_user = await crud_users.get(db=db, username=current_user["username"], is_deleted=False, schema_to_select=UserRead)
    if db_user is None:
        raise NotFoundException("User Not Found!")
    
    if current_user["id"] != db_user["id"]:
        raise ForbiddenException()    

    post_internal_dict = post.model_dump()
    post_internal_dict["author_id"] = db_user["id"]
    post_internal_dict["author_name"] = db_user["username"]

    post_internal = PostCreateInternal(**post_internal_dict)
    created_post = await crud_posts.create(db=db, object=post_internal, schema_to_select=PostRead)

    if created_post is None:
        raise NotFoundException("Failed to create the post!!!")
    
    return created_post


@router.put("/posts/{post_id}", response_model=PostRead, status_code=201)
async def update_post(post_id:int, post:PostUpdate, current_user:Annotated[SessionDep, Depends(get_current_active_user)], db: SessionDep) -> dict[str, Any]:
    db_user = await crud_users.get(db=db, username=current_user["username"], is_deleted=False, schema_to_select=UserRead)
    if not db_user:
        raise NotFoundException("User Not Found!!!")
    
    if current_user["id"] != db_user["id"]:
        raise ForbiddenException()
    
    db_post = await crud_posts.get(db=db, id=post_id, is_deleted=False, schema_to_select=PostRead)
    if current_user["username"] != db_post["author_name"]:
        raise ForbiddenException()
    
    post_internal_dict = post.model_dump(exclude_unset=True)
    post_internal_dict["updated_at"] = datetime.now(UTC)
    post_internal = PostUpdateInternal(**post_internal_dict)
    updated_post = await crud_posts.update(db=db, id=post_id, object=post_internal, schema_to_select=PostRead, return_as_model=True)

    if updated_post is None:
        raise NotFoundException("Failed to update the post!!!")
    
    return updated_post


@router.delete("/posts/{post_id}")
async def delete_post(post_id:int, current_user: Annotated[dict, Depends(get_current_active_user)], db: SessionDep) -> dict[str, str]:
    db_user = await crud_users.get(db=db, username=current_user["username"], is_deleted=False, schema_to_select=UserRead)
    if not db_user:
        raise NotFoundException("User Not Found!!!")


    db_post = await crud_posts.get(db=db, id=post_id, is_deleted=False, schema_to_select=PostRead)
    if db_post is None:
        raise NotFoundException("Post Not Found!!!")
    
    if current_user["id"] != db_post["author_id"]:
        raise ForbiddenException()

    await crud_posts.db_delete(db=db, id=post_id)

    return {"message": f"{db_post["title"]} has been successfully deleted."} 