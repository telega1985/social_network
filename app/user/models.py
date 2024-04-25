import uuid
import enum
from typing import Optional

from app.database import Base, intpk, created_at
from sqlalchemy import ForeignKey, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship


class Gender(enum.Enum):
    male = "Мужской"
    female = "Женский"


class User(Base):
    __tablename__ = "user"

    id: Mapped[intpk]
    email: Mapped[str] = mapped_column(unique=True, index=True)
    hashed_password: Mapped[str]

    # profile
    first_name: Mapped[Optional[str]]
    last_name: Mapped[Optional[str]]
    description: Mapped[Optional[str]]
    location: Mapped[Optional[str]]
    gender: Mapped[Gender] = mapped_column(default=Gender.male)
    image: Mapped[Optional[str]]
    created_at: Mapped[created_at]
    is_active: Mapped[bool] = mapped_column(default=True)
    is_verified: Mapped[bool] = mapped_column(default=False)
    is_superuser: Mapped[bool] = mapped_column(default=False)

    posts: Mapped[list["Post"]] = relationship(back_populates="user")
    liked_posts: Mapped[list["Post"]] = relationship(
        secondary="post_likes_association", back_populates="liked_by_users"
    )

    def __str__(self) -> str:
        return f"Пользователь {self.email}"


class RefreshSession(Base):
    __tablename__ = "refresh_session"

    id: Mapped[intpk]
    refresh_token: Mapped[uuid.UUID] = mapped_column(UUID, index=True)
    expires_in: Mapped[int]
    created_at: Mapped[created_at]
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"))


class VerificationSession(Base):
    __tablename__ = "verification_session"

    id: Mapped[intpk]
    verification_token: Mapped[uuid.UUID] = mapped_column(UUID, index=True)
    expires_in: Mapped[int]
    created_at: Mapped[created_at]
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"))
