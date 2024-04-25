import re
from typing import Optional

from app.database import async_session_maker
from app.exceptions import CannotAddDataToDatabase, HashtagNotFound
from app.image_utils import image_add_origin
from app.post.models import Post
from app.post.schemas import SPostCreate, SPostImageInfo, SPostInfo
from app.post.dao import PostDAO, PostImageDAO, HashtagDAO, PostHashtagAssociationDAO
from app.logger import logger
from fastapi import UploadFile, File
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession


class PostService:
    @classmethod
    async def process_hashtags(cls, session: AsyncSession, new_post: Post) -> list[int]:
        regex = r"#\w+"
        matches = re.findall(regex, new_post.content)
        names = [match[1:] for match in matches]

        existing_hashtags = await HashtagDAO.db_one_hashtag_in(session, names)

        existing_names = []
        hashtags_to_add_in_post = []

        for hashtag in existing_hashtags:
            existing_names.append(hashtag.name)
            hashtags_to_add_in_post.append(hashtag.id)

        # составляем список хештегов, которых нет в базе

        new_hashtags = [{"name": name} for name in names if name not in existing_names]

        new_hashtags_ids = await HashtagDAO.add_many(session, data=new_hashtags, return_ids=True)
        hashtags_to_add_in_post.extend(new_hashtags_ids)

        return hashtags_to_add_in_post

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

                new_post = await PostDAO.add(
                    session,
                    **new_post_data,
                    image_id=photo_id,
                    user_id=user_id
                )

                hashtags = await cls.process_hashtags(session, new_post)

                associations_to_add = []

                for hashtag in hashtags:
                    associations_to_add.append({"post_id": new_post.id, "hashtag_id": hashtag})

                await PostHashtagAssociationDAO.add_many(session, data=associations_to_add)

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
    async def service_get_posts_from_hashtag(cls, hashtag_name: str) -> list[SPostInfo]:
        """
        Получаем посты из хэштегов
        """
        async with async_session_maker() as session:
            hashtag = await HashtagDAO.db_get_posts_from_hashtag(session, hashtag_name)

            if not hashtag:
                raise HashtagNotFound

        return hashtag.posts

    @classmethod
    async def service_get_random_posts_for_feed(cls, page: int = 1, limit: int = 10, hashtag: str = None):
        """
        Получаем случайные посты для пользователей в ленте. Возвращаем последние посты для всех пользователей
        """
        async with async_session_maker() as session:
            total_posts = await PostDAO.db_total_posts(session)

            offset = (page - 1) * limit

            if offset >= total_posts:
                return []

            posts = await PostDAO.db_get_posts_join_user(session, hashtag)

        result = []

        for post, first_name in posts:
            post_dict = post.__dict__
            post_dict["first_name"] = first_name
            result.append(post_dict)

        return result
