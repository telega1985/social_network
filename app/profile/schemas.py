from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.post.schemas import SPostProfile
from app.user.schemas import SUserInfo, SFollowInfo


class SProfileUser(SUserInfo):
    followers_count: int = 0
    following_count: int = 0
    posts: list[SPostProfile]
    followers: list[SFollowInfo]
    following: list[SFollowInfo]

    model_config = ConfigDict(from_attributes=True)


class SFollowProfile(BaseModel):
    image: Optional[str]
    first_name: Optional[str] = Field(None)

    model_config = ConfigDict(from_attributes=True)


class SFollowersList(BaseModel):
    followers: list[SFollowProfile] = []

    model_config = ConfigDict(from_attributes=True)


class SFollowingList(BaseModel):
    following: list[SFollowProfile] = []

    model_config = ConfigDict(from_attributes=True)
