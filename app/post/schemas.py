from datetime import datetime

from pydantic import BaseModel, ConfigDict
from typing import Optional

from app.user.schemas import SUserLiked


class SPostCreate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    image_id: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


class SPostImageInfo(BaseModel):
    id: int
    user_id: int
    image: Optional[str]

    model_config = ConfigDict(from_attributes=True)


class SHashtag(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)


class SHashtagPosts(SPostCreate):
    id: int
    user_id: int
    created_at: datetime
    likes_count: Optional[int] = 0


class SPostRandom(SHashtagPosts):
    first_name: Optional[str]


class SPostRandomWithPostAssociation(SPostRandom):
    post_id: int
    hashtag_id: int


class SPostProfile(SHashtagPosts):
    pass


class SPostInfo(SPostProfile):
    hashtags: list[SHashtag]
    image: Optional[SPostImageInfo]
    liked_by_users: list[SUserLiked]
