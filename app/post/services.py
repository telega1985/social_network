import re
from typing import Optional, Union

from app.activity.models import Activity
from app.database import async_session_maker
from app.exceptions import CannotAddDataToDatabase, HashtagNotFound, PostNotFound, UserNotFound
from app.image_utils import image_add_origin
from app.post.models import Post
from app.post.schemas import (
    SPostCreate, SPostImageInfo, SPostInfo, SHashtagPosts, SPostRandom,
    SPostRandomWithPostAssociation
)
from app.post.dao import PostDAO, PostImageDAO, HashtagDAO
from app.logger import logger
from fastapi import UploadFile, File
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.user.dao import UserDAO
from app.user.schemas import SUserLiked


class PostService:
    @classmethod
    async def service_process_hashtags(cls, session: AsyncSession, new_post: Post):
        """
        Выбираем хэштеги из постов и создаем новые, если их еще нет в БД.
        """
        regex = r"#\w+"
        matches = re.findall(regex, new_post.content)
        names = [match[1:] for match in matches]

        existing_hashtags = await HashtagDAO.db_one_hashtag_in(session, names)
        existing_hashtags_names = {hashtag.name for hashtag in existing_hashtags}
        new_hashtags_names = list(set(names) - existing_hashtags_names)

        if new_hashtags_names:
            new_hashtags = [{"name": name} for name in new_hashtags_names]
            existing_hashtags += await HashtagDAO.add_many(session, data=new_hashtags)

        new_post.hashtags = existing_hashtags

    @classmethod
    async def service_upload_photo_for_post(
            cls, user_id: int, image: UploadFile = File(...)
    ) -> Optional[SPostImageInfo]:
        """
        Загружаем фото для поста.
        """
        path_folder = f"app/static/post_images/post_{user_id}"
        path_file = await image_add_origin(path_folder, image)
        relative_path = f"/post_images/post_{user_id}/{path_file}"

        async with async_session_maker() as session:
            new_photo = await PostImageDAO.add(
                session,
                image=relative_path,
                user_id=user_id
            )
            await session.commit()

        return new_photo

    @classmethod
    async def service_create_post(cls, user_id: int, post: SPostCreate):
        """
        Создаем пост, включая картинку и хэштеги, если они есть
        """
        try:
            async with async_session_maker() as session:
                photo_id = None

                if post.image_id:
                    photo = await PostImageDAO.find_one_or_none(session, id=post.image_id)
                    if photo:
                        photo_id = photo.id

                new_post_data = post.model_dump(exclude={"image_id"})

                new_post = Post(
                    **new_post_data,
                    image_id=photo_id,
                    user_id=user_id
                )

                await cls.service_process_hashtags(session, new_post)

                session.add(new_post)

                await session.commit()

            return new_post
        except (SQLAlchemyError, Exception) as e:
            msg = ""
            if isinstance(e, SQLAlchemyError):
                msg = "Database Exc"
            elif isinstance(e, Exception):
                msg = "Unknown Exc"

            msg += ": Cannot insert data into table"

            logger.error(msg, exc_info=True)

            raise CannotAddDataToDatabase

    @classmethod
    async def service_get_user_posts(cls, user_id: int) -> list[SPostInfo]:
        """
        Получаем список всех постов пользователя
        """
        async with async_session_maker() as session:
            return await PostDAO.db_get_user_posts(session, user_id)

    @classmethod
    async def service_get_posts_from_hashtag(cls, hashtag_name: str) -> list[SHashtagPosts]:
        """
        Получаем посты из хэштегов
        """
        async with async_session_maker() as session:
            hashtag = await HashtagDAO.db_get_posts_from_hashtag(session, hashtag_name)

        if not hashtag:
            raise HashtagNotFound

        return hashtag.posts

    @classmethod
    async def service_get_random_posts_for_feed(
            cls, page: int = 1, limit: int = 10, hashtag: str = None
    ) -> Union[list[SPostRandom], list[SPostRandomWithPostAssociation]]:
        """
        Получаем случайные посты для пользователей в ленте. Возвращаем последние посты для всех пользователей
        """
        async with async_session_maker() as session:
            total_posts = await PostDAO.db_total_posts(session)

            offset = (page - 1) * limit

            if offset >= total_posts:
                return []

            posts = await PostDAO.db_get_posts_join_user(session, offset, limit, hashtag)

        if not hashtag:
            return [SPostRandom(**post) for post in posts]

        return [SPostRandomWithPostAssociation(**post) for post in posts]

    @classmethod
    async def service_get_post_by_id(cls, post_id: int) -> Optional[SPostInfo]:
        """
        Получаем пост по id
        """
        async with async_session_maker() as session:
            return await PostDAO.db_get_post_by_id(session, post_id)

    @classmethod
    async def service_delete_post_by_id(cls, post_id: int, user_id: int):
        """
        Удаляем пост по id
        """
        async with async_session_maker() as session:
            post = await PostDAO.find_one_or_none(session, id=post_id)

            if post:
                await PostDAO.delete(session, id=post_id, user_id=user_id)

            await session.commit()

    @classmethod
    async def service_get_post_and_user(cls, session: AsyncSession, post_id: int, username: str):
        post = await PostDAO.db_get_post_by_id(session, post_id)

        if not post:
            raise PostNotFound

        user = await UserDAO.find_one_or_none(session, first_name=username)

        if not user:
            raise UserNotFound

        return post, user

    @classmethod
    async def service_like_post(cls, post_id: int, username: str):
        async with async_session_maker() as session:
            post, user = await cls.service_get_post_and_user(session, post_id, username)

            if user in post.liked_by_users:
                return False, "Пост уже понравился"

            post.liked_by_users.append(user)
            post.likes_count = len(post.liked_by_users)

            # TO DO activity of like

            activity = Activity(
                username=post.user.first_name,
                liked_post_id=post_id,
                username_like=username,
                liked_post_image_id=post.image_id
            )

            session.add(activity)

            await session.commit()

        return post

    @classmethod
    async def service_unlike_post(cls, post_id: int, username: str):
        async with async_session_maker() as session:
            post, user = await cls.service_get_post_and_user(session, post_id, username)

            if user not in post.liked_by_users:
                return False, "Пост еще не лайкали"

            post.liked_by_users.remove(user)
            post.likes_count = len(post.liked_by_users)

            await session.commit()

        return post

    @classmethod
    async def service_liked_users_post(cls, post_id: int) -> list[SUserLiked]:
        async with async_session_maker() as session:
            post = await PostDAO.db_get_post_by_id(session, post_id)

            if not post:
                raise PostNotFound

        return post.liked_by_users
