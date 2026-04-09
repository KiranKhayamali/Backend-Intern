from fastcrud import FastCRUD
from ..models.posts import Post 
from ..schemas.post import PostCreateInternal, PostRead, PostUpdate, PostUpdateInternal, PostDelete


CRUDPosts = FastCRUD[Post, PostCreateInternal, PostRead, PostUpdate, PostUpdateInternal, PostDelete]
crud_posts = CRUDPosts(Post)