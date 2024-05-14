from typing import Optional, Union

from fastapi import APIRouter, status, Depends, UploadFile, File

from app.post.schemas import (
    SPostCreate, SPostInfo, SPostImageInfo, SHashtagPosts, SPostRandom,
    SPostRandomWithPostAssociation
)
from app.post.services import PostService
from app.user.dependencies import get_current_active_user
from app.user.models import User
from app.user.schemas import SUserLiked

router_post = APIRouter(
    prefix="/posts",
    tags=["Посты"]
)


@router_post.post("", status_code=status.HTTP_201_CREATED)
async def create_post(post: SPostCreate, current_user: User = Depends(get_current_active_user)):
    return await PostService.service_create_post(current_user.id, post)


@router_post.post("/post-image", status_code=status.HTTP_201_CREATED)
async def upload_photo_for_post(
        image: UploadFile = File(...),
        current_user: User = Depends(get_current_active_user)
) -> Optional[SPostImageInfo]:
    return await PostService.service_upload_photo_for_post(current_user.id, image)


@router_post.get("/all-post-users")
async def get_user_posts(current_user: User = Depends(get_current_active_user)) -> list[SPostInfo]:
    return await PostService.service_get_user_posts(current_user.id)


@router_post.get("/hashtag-posts")
async def get_posts_from_hashtag(hashtag_name: str) -> list[SHashtagPosts]:
    return await PostService.service_get_posts_from_hashtag(hashtag_name)


@router_post.get("/feed")
async def get_random_posts_for_feed(
        page: int = 1, limit: int = 10, hashtag: str = None
) -> Union[list[SPostRandom], list[SPostRandomWithPostAssociation]]:
    return await PostService.service_get_random_posts_for_feed(page, limit, hashtag)


@router_post.post("/like", status_code=status.HTTP_201_CREATED)
async def like_post(post_id: int, current_user: User = Depends(get_current_active_user)):
    return await PostService.service_like_post(post_id, current_user.first_name)


@router_post.post("/unlike", status_code=status.HTTP_201_CREATED)
async def unlike_post(post_id: int, current_user: User = Depends(get_current_active_user)):
    return await PostService.service_unlike_post(post_id, current_user.first_name)


@router_post.delete("", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post_by_id(post_id: int, current_user: User = Depends(get_current_active_user)):
    await PostService.service_delete_post_by_id(post_id, current_user.id)


@router_post.get("/liked-post")
async def liked_users_post(post_id: int) -> list[SUserLiked]:
    return await PostService.service_liked_users_post(post_id)


@router_post.get("/{post_id}")
async def get_post_by_id(post_id: int) -> Optional[SPostInfo]:
    return await PostService.service_get_post_by_id(post_id)
