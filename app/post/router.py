from typing import Optional

from fastapi import APIRouter, status, Depends, UploadFile, File

from app.post.schemas import SPostCreate, SPostInfo, SPostImageInfo
from app.post.services import PostService
from app.user.dependencies import get_current_active_user
from app.user.models import User

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


@router_post.get("")
async def get_user_posts(current_user: User = Depends(get_current_active_user)) -> list[SPostInfo]:
    return await PostService.service_get_user_posts(current_user.id)
