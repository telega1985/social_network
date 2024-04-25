from datetime import datetime

from pydantic import BaseModel, ConfigDict
from typing import Optional


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


class SPostInfo(SPostCreate):
    id: int
    user_id: int
    image: Optional[SPostImageInfo]
    hashtags: list[SHashtag]
    created_at: datetime
    likes_count: Optional[int] = 0

    model_config = ConfigDict(from_attributes=True)
