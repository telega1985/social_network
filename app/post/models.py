from typing import Optional

from app.database import Base, intpk, created_at
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship


class PostHashtagAssociation(Base):
    __tablename__ = "post_hashtag_association"

    post_id: Mapped[int] = mapped_column(ForeignKey("post.id"), primary_key=True)
    hashtag_id: Mapped[int] = mapped_column(ForeignKey("hashtag.id"), primary_key=True)


class PostLikesAssociation(Base):
    __tablename__ = "post_likes_association"

    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), primary_key=True)
    post_id: Mapped[int] = mapped_column(ForeignKey("post.id"), primary_key=True)


class PostImage(Base):
    __tablename__ = "post_image"

    id: Mapped[intpk]
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"))
    image: Mapped[Optional[str]]

    post: Mapped["Post"] = relationship(back_populates="image")

    def __str__(self) -> str:
        return self.image


class Post(Base):
    __tablename__ = "post"

    id: Mapped[intpk]
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"))
    title: Mapped[Optional[str]]
    content: Mapped[Optional[str]]
    image_id: Mapped[Optional[int]] = mapped_column(ForeignKey("post_image.id", ondelete="SET NULL"))
    created_at: Mapped[created_at]
    likes_count: Mapped[Optional[int]] = mapped_column(default=0)

    image: Mapped["PostImage"] = relationship(back_populates="post")
    user: Mapped["User"] = relationship(back_populates="posts")
    hashtags: Mapped[list["Hashtag"]] = relationship(secondary="post_hashtag_association", back_populates="posts")
    liked_by_users: Mapped[list["User"]] = relationship(
        secondary="post_likes_association", back_populates="liked_posts"
    )

    def __str__(self) -> str:
        return self.title


class Hashtag(Base):
    __tablename__ = "hashtag"

    id: Mapped[intpk]
    name: Mapped[str] = mapped_column(index=True)

    posts: Mapped[list["Post"]] = relationship(secondary="post_hashtag_association", back_populates="hashtags")

    def __str__(self) -> str:
        return self.name
