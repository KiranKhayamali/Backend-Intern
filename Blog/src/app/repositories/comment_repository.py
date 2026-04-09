from fastcrud import FastCRUD 
from ..models.comments import Comment
from ..schemas.comment import CommentCreateInternal, CommentRead, CommentUpdate, CommentUpdateInternal, CommentDelete


CRUDComment = FastCRUD[Comment, CommentCreateInternal, CommentRead, CommentUpdate, CommentUpdateInternal, CommentDelete]
crud_comments = CRUDComment(Comment)