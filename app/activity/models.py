from typing import Optional

from app.database import Base, intpk, created_at
from sqlalchemy.orm import Mapped


class Activity(Base):
    __tablename__ = "activities"

    id: Mapped[intpk]
    username: Mapped[str]
    timestamp: Mapped[created_at]
    liked_post_id: Mapped[Optional[int]]
    username_like: Mapped[Optional[str]]
    liked_post_image_id: Mapped[Optional[int]]
    followed_username: Mapped[Optional[str]]
    followed_user_image: Mapped[Optional[str]]

    def __str__(self) -> str:
        return self.username
