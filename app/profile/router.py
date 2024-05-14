from typing import Optional

from fastapi import APIRouter, status, Depends

from app.profile.schemas import SProfileUser, SFollowersList, SFollowingList
from app.profile.services import ProfileService
from app.user.dependencies import get_current_active_user
from app.user.models import User

router_profile = APIRouter(
    prefix="/profile",
    tags=["Profile"]
)


@router_profile.get("/user/{username}")
async def get_profile(username: str) -> Optional[SProfileUser]:
    return await ProfileService.service_get_existing_user(username)


@router_profile.post("/follow/{username}", status_code=status.HTTP_201_CREATED)
async def follow(username: str, current_user: User = Depends(get_current_active_user)):
    return await ProfileService.service_follow(current_user.first_name, username)


@router_profile.post("/unfollow/{username}", status_code=status.HTTP_201_CREATED)
async def unfollow(username: str, current_user: User = Depends(get_current_active_user)):
    return await ProfileService.service_unfollow(current_user.first_name, username)


@router_profile.get("/followers")
async def get_followers(current_user: User = Depends(get_current_active_user)) -> list[SFollowersList]:
    return await ProfileService.service_get_followers(current_user.id)


@router_profile.get("/following")
async def get_following(current_user: User = Depends(get_current_active_user)) -> list[SFollowingList]:
    return await ProfileService.service_get_following(current_user.id)
