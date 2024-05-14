from datetime import datetime

from pydantic import BaseModel, ConfigDict
from typing import Optional


class SActivityBase(BaseModel):
    username: str
    liked_post_id: Optional[int] = None
    username_like: Optional[str] = None
    followed_username: Optional[str] = None
    liked_post_image_id: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


class SActivity(SActivityBase):
    timestamp: datetime
