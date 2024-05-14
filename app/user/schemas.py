import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, ConfigDict
from app.user.models import Gender
from typing import Optional


class SFollowInfo(BaseModel):
    follower_id: int
    following_id: int


class SUserLiked(BaseModel):
    id: int
    first_name: Optional[str] = Field(None)

    model_config = ConfigDict(from_attributes=True)


class SUserCreate(BaseModel):
    email: EmailStr
    password: str

    model_config = ConfigDict(from_attributes=True)


class SUserBase(BaseModel):
    first_name: Optional[str] = Field(None)
    last_name: Optional[str] = Field(None)
    description: Optional[str] = Field(None)
    location: Optional[str] = Field(None)
    gender: Gender
    is_active: bool = Field(True)
    is_verified: bool = Field(False)
    is_superuser: bool = Field(False)

    model_config = ConfigDict(from_attributes=True)


class SUserUpdate(SUserBase):
    password: Optional[str] = None


class SUserInfo(SUserBase):
    id: int
    email: EmailStr
    created_at: datetime
    image: Optional[str]


class SToken(BaseModel):
    access_token: str
    refresh_token: uuid.UUID

    model_config = ConfigDict(from_attributes=True)
