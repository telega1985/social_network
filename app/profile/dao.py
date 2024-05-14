from sqlalchemy.ext.asyncio import AsyncSession

from app.dao.base import BaseDAO

from sqlalchemy import select
from sqlalchemy.orm import selectinload, joinedload

from app.user.models import Follow, User


class ProfileUserDAO(BaseDAO):
    model = User

    @classmethod
    async def db_get_profile(cls, session: AsyncSession, **filter_by):
        query = (
            select(cls.model)
            .options(selectinload(cls.model.posts))
            .options(selectinload(cls.model.followers))
            .options(selectinload(cls.model.following))
            .filter_by(**filter_by)
        )
        result = await session.execute(query)
        return result.scalars().one_or_none()


class ProfileFollowDAO(BaseDAO):
    model = Follow

    @classmethod
    async def db_get_followers_with_user(cls, session: AsyncSession, user_id: int):
        query = (
            select(cls.model)
            .options(joinedload(cls.model.follower))
            .filter_by(following_id=user_id)
        )
        result = await session.execute(query)
        return result.scalars().all()

    @classmethod
    async def db_get_following_with_user(cls, session: AsyncSession, user_id: int):
        query = (
            select(cls.model)
            .options(joinedload(cls.model.following))
            .filter_by(follower_id=user_id)
        )
        result = await session.execute(query)
        return result.scalars().all()
