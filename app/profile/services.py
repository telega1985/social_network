from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.activity.dao import ActivityDAO
from app.database import async_session_maker
from app.exceptions import UserNotFound
from app.profile.dao import ProfileUserDAO, ProfileFollowDAO
from app.profile.schemas import SProfileUser, SFollowersList, SFollowingList


class ProfileService:
    @classmethod
    async def service_existing_user(cls, session: AsyncSession, username: str) -> Optional[SProfileUser]:
        user = await ProfileUserDAO.db_get_profile(session, first_name=username)

        if not user:
            raise UserNotFound

        return user

    @classmethod
    async def service_get_existing_user(cls, username: str) -> Optional[SProfileUser]:
        async with async_session_maker() as session:
            return await cls.service_existing_user(session, username)

    @classmethod
    async def service_get_follower_and_following(cls, session: AsyncSession, follower: str, following: str):
        db_follower = await cls.service_existing_user(session, follower)
        db_following = await cls.service_existing_user(session, following)

        if not (db_follower or db_following):
            return False

        return db_follower, db_following

    @classmethod
    async def service_follow(cls, follower: str, following: str):
        """ Подписаться на кого-то
        """
        async with async_session_maker() as session:
            db_follower, db_following = await cls.service_get_follower_and_following(session, follower, following)

            db_follow = await ProfileFollowDAO.find_one_or_none(
                session, follower_id=db_follower.id, following_id=db_following.id
            )

            if db_follow:
                return False

            await ProfileFollowDAO.add(
                session, follower_id=db_follower.id, following_id=db_following.id
            )

            db_follower.following_count += 1
            db_following.followers_count += 1

            await ActivityDAO.add(
                session,
                username=following,
                followed_username=db_follower.first_name,
                followed_user_image=db_follower.image
            )

            await session.commit()

        return {"message": "Вы успешно подписались"}

    @classmethod
    async def service_unfollow(cls, follower: str, following: str):
        """ Отписаться от кого-то
        """
        async with async_session_maker() as session:
            db_follower, db_following = await cls.service_get_follower_and_following(session, follower, following)

            db_follow = await ProfileFollowDAO.find_one_or_none(
                session, follower_id=db_follower.id, following_id=db_following.id
            )

            if not db_follow:
                return False

            await ProfileFollowDAO.delete(session, follower_id=db_follower.id)

            db_follower.following_count -= 1
            db_following.followers_count -= 1

            await session.commit()

        return {"message": "Вы успешно отписались"}

    @classmethod
    async def service_get_followers(cls, user_id: int) -> list[SFollowersList]:
        """ Получаем подписчиков
        """
        async with async_session_maker() as session:
            db_followers = await ProfileFollowDAO.db_get_followers_with_user(session, user_id)

            followers = []

            for user in db_followers:
                followers.append(
                    {
                        "image": user.follower.image,
                        "first_name": user.follower.first_name
                    }
                )

        return [SFollowersList(followers=followers)]

    @classmethod
    async def service_get_following(cls, user_id: int) -> list[SFollowingList]:
        """ Получаем на кого подписались
        """
        async with async_session_maker() as session:
            db_following = await ProfileFollowDAO.db_get_following_with_user(session, user_id)

            following = []

            for user in db_following:
                following.append(
                    {
                        "image": user.following.image,
                        "first_name": user.following.first_name
                    }
                )

        return [SFollowingList(following=following)]
