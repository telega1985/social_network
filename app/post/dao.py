from app.dao.base import BaseDAO
from app.post.models import Post, PostImage, Hashtag, PostHashtagAssociation

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload

from app.user.models import User


class PostDAO(BaseDAO):
    model = Post

    @classmethod
    async def db_get_user_posts(cls, session: AsyncSession, user_id: int):
        query = (
            select(cls.model)
            .options(joinedload(cls.model.image))
            .options(selectinload(cls.model.hashtags))
            .options(selectinload(cls.model.liked_by_users))
            .order_by(cls.model.created_at.desc())
            .filter_by(user_id=user_id)
        )
        result = await session.execute(query)
        return result.scalars().all()

    @classmethod
    async def db_get_post_by_id(cls, session: AsyncSession, post_id: int):
        query = (
            select(cls.model)
            .options(joinedload(cls.model.image))
            .options(selectinload(cls.model.hashtags))
            .options(selectinload(cls.model.liked_by_users))
            .options(joinedload(cls.model.user))
            .filter_by(id=post_id)
        )
        result = await session.execute(query)
        return result.scalars().one_or_none()

    @classmethod
    async def db_total_posts(cls, session: AsyncSession):
        query = select(func.count(cls.model.id))
        result = await session.execute(query)
        result: int = result.scalar()
        return result

    @classmethod
    async def db_get_posts_join_user(cls, session: AsyncSession, offset: int, limit: int = 10, hashtag: str = None):
        posts_for_users = (
            select(
                cls.model.__table__.columns,
                User.first_name
            )
            .join(User, User.id == cls.model.user_id, isouter=True)
            .order_by(cls.model.created_at.desc())
            .cte("posts_for_users")
        )

        if hashtag:
            posts = (
                select(posts_for_users, PostHashtagAssociation.__table__.columns)
                .join(PostHashtagAssociation, posts_for_users.c.id == PostHashtagAssociation.post_id, isouter=True)
                .join(Hashtag, Hashtag.id == PostHashtagAssociation.hashtag_id, isouter=True)
                .where(Hashtag.name == hashtag)
                .offset(offset)
                .limit(limit)
            )
        else:
            posts = select(posts_for_users).offset(offset).limit(limit)

        result = await session.execute(posts)
        return result.mappings().all()


class PostImageDAO(BaseDAO):
    model = PostImage


class HashtagDAO(BaseDAO):
    model = Hashtag

    @classmethod
    async def db_get_posts_from_hashtag(cls, session: AsyncSession, hashtag_name: str):
        query = (
            select(cls.model)
            .options(selectinload(cls.model.posts))
            .filter_by(name=hashtag_name)
        )
        result = await session.execute(query)
        return result.scalars().one_or_none()

    @classmethod
    async def db_one_hashtag_in(cls, session: AsyncSession, names: list):
        query = (
            select(cls.model)
            .where(cls.model.name.in_(names))
        )
        result = await session.execute(query)
        return result.scalars().all()
