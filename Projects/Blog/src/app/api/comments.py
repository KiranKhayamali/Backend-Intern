from typing import Annotated, Any
from fastapi import APIRouter, Depends
from fastcrud import PaginatedListResponse, compute_offset, paginated_response
from datetime import datetime, UTC

from ..core.dependencies import SessionDep, get_current_active_user
from ..core.exceptions.http_exceptions import NotFoundException, ForbiddenException
from ..schemas.comment import (
    CommentRead,
    CommentCreate,
    CommentCreateInternal,
    CommentUpdate,
    CommentUpdateInternal,
)
from ..schemas.user import UserRead
from ..schemas.post import PostRead
from ..repositories.comment_repository import crud_comments
from ..repositories.user_repository import crud_users
from ..repositories.post_repository import crud_posts

router = APIRouter(tags=["comments"])


@router.post("/posts/{post_id}/comments", response_model=CommentRead, status_code=201)
async def write_comment(
    post_id: int,
    comment: CommentCreate,
    current_user: Annotated[SessionDep, Depends(get_current_active_user)],
    db: SessionDep,
) -> dict[str, Any]:
    if current_user is None:
        return {"message": "User Not Logged In, Login First!!!"}

    db_user = await crud_users.get(
        db=db,
        username=current_user["username"],
        is_deleted=False,
        schema_to_select=UserRead,
    )
    if db_user is None:
        raise NotFoundException("User Not Found!!!")

    db_post = await crud_posts.get(
        db=db, id=post_id, is_deleted=False, schema_to_select=PostRead
    )
    if db_post is None:
        raise NotFoundException("Post Not Found!!!")

    comment_internal_dict = comment.model_dump()
    comment_internal_dict["author_id"] = db_user["id"]
    comment_internal_dict["post_id"] = db_post["id"]
    comment_internal_dict["author_name"] = db_user["username"]
    comment_internal_dict["post_title"] = db_post["title"]

    comment_internal = CommentCreateInternal(**comment_internal_dict)
    created_comment = await crud_comments.create(
        db=db, object=comment_internal, schema_to_select=CommentRead
    )

    if created_comment is None:
        raise NotFoundException("Failed to Write the comment to the post!!!")

    return created_comment


@router.get("/comments", response_model=PaginatedListResponse[CommentRead])
async def read_comments_from_all_posts(
    db: SessionDep, page: int = 1, items_per_page: int = 10
) -> dict[str, Any]:
    comments_data = await crud_comments.get_multi(
        db=db,
        offset=compute_offset(page, items_per_page),
        limit=items_per_page,
        is_deleted=False,
    )

    response: dict[str, Any] = paginated_response(
        crud_data=comments_data, page=page, items_per_page=items_per_page
    )
    return response


@router.put("/comments/{comment_id}", response_model=CommentRead, status_code=201)
async def update_comment(
    comment_id: int,
    comment: CommentUpdate,
    current_user: Annotated[SessionDep, Depends(get_current_active_user)],
    db: SessionDep,
) -> dict[str, Any]:
    db_user = await crud_users.get(
        db=db,
        username=current_user["username"],
        is_deleted=False,
        schema_to_select=UserRead,
    )
    if not db_user:
        raise NotFoundException("User Not Found!!!")

    if current_user["id"] != db_user["id"]:
        raise ForbiddenException()

    db_comment = await crud_comments.get(
        db=db, id=comment_id, is_deleted=False, schema_to_select=CommentRead
    )
    if current_user["username"] != db_comment["author_name"]:
        raise ForbiddenException()

    comment_internal_dict = comment.model_dump(exclude_unset=True)
    comment_internal_dict["updated_at"] = datetime.now(UTC)
    comment_internal = CommentUpdateInternal(**comment_internal_dict)
    updated_comment = await crud_comments.update(
        db=db,
        id=comment_id,
        object=comment_internal,
        schema_to_select=CommentRead,
        return_as_model=True,
    )
    if updated_comment is None:
        raise NotFoundException("Failed to update the comment!!!")

    return updated_comment


@router.delete("/comments/{comment_id}")
async def delete_comment(
    comment_id: int,
    current_user: Annotated[SessionDep, Depends(get_current_active_user)],
    db: SessionDep,
) -> dict[str, str]:
    db_user = await crud_users.get(
        db=db,
        username=current_user["username"],
        is_deleted=False,
        schema_to_select=UserRead,
    )
    if not db_user:
        raise NotFoundException("User Not Found!!!")

    db_comment = await crud_comments.get(
        db=db, id=comment_id, is_deleted=False, schema_to_select=CommentRead
    )
    if db_comment is None:
        raise NotFoundException("Comment Not Found!!!")

    if current_user["id"] != db_comment["author_id"]:
        raise ForbiddenException()

    await crud_comments.delete(db=db, id=comment_id)

    return {"message": f"Comment ID:{comment_id} has been sucessfully deleted."}
