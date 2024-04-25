from typing import Optional
from datetime import timedelta

from app.config import settings
from app.database import async_session_maker
from app.exceptions import UserAlreadyExistsException, UserNotFound
from app.image_utils import image_add_origin
from app.tasks.tasks import send_email_report_dashboard

from app.user.auth import AuthService
from app.user.dao import UserDAO, VerificationSessionDAO
from app.user.models import User
from app.user.schemas import SUserCreate, SUserUpdate, SUserInfo
from fastapi import UploadFile, File


class UserService:
    @classmethod
    async def service_create_new_user(cls, user: SUserCreate) -> SUserInfo:
        async with async_session_maker() as session:
            existing_user = await UserDAO.find_one_or_none(session, email=user.email)

            if existing_user:
                raise UserAlreadyExistsException

            hashed_password = AuthService.get_password_hash(user.password)

            db_user = await UserDAO.add(
                session,
                **user.model_dump(exclude={"password"}),
                hashed_password=hashed_password
            )

            verification_token = AuthService.create_verification_token()
            verification_token_expires = timedelta(minutes=settings.VERIFICATION_TOKEN_EXPIRE_MINUTES)

            db_verification = await VerificationSessionDAO.add(
                session,
                user_id=db_user.id,
                verification_token=verification_token,
                expires_in=verification_token_expires.total_seconds()
            )

            await session.commit()

            user_dict = {"email": db_user.email}

            send_email_report_dashboard.delay(user_dict, db_verification.verification_token)

        return db_user

    @classmethod
    async def service_get_authorization_user(cls, user_id: int) -> Optional[SUserInfo]:
        async with async_session_maker() as session:
            db_user = await UserDAO.find_one_or_none(session, id=user_id)

        if not db_user:
            raise UserNotFound

        return db_user

    @classmethod
    async def service_upload_image_for_user(cls, user_id: int, image: UploadFile = File(...)):
        path_folder = f"app/static/user_images/user_{user_id}"
        path_file = await image_add_origin(path_folder, image)
        relative_path = f"/user_images/user_{user_id}/{path_file}"

        async with async_session_maker() as session:
            await UserDAO.update(
                session,
                User.id == user_id,
                image=relative_path
            )
            await session.commit()

        return {"message": "Изображение успешно загружено"}

    @classmethod
    async def service_update_user(cls, user_id: int, user: SUserUpdate) -> SUserInfo:
        async with async_session_maker() as session:
            db_user = await UserDAO.find_one_or_none(session, id=user_id)

            if not db_user:
                raise UserNotFound

            update_data = user.model_dump(
                exclude={"is_active", "is_verified", "is_superuser", "password"},
                exclude_unset=True
            )

            if user.password:
                update_data["hashed_password"] = AuthService.get_password_hash(user.password)

            user_update = await UserDAO.update(
                session,
                User.id == user_id,
                **update_data
            )

            await session.commit()

            return user_update

    @classmethod
    async def service_delete_user(cls, user_id: int):
        async with async_session_maker() as session:
            await UserDAO.delete(session, id=user_id)
            await session.commit()

    @classmethod
    async def service_get_users_list(cls) -> list[SUserInfo]:
        async with async_session_maker() as session:
            return await UserDAO.find_all(session)
