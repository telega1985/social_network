import uuid

from fastapi import APIRouter, status, Response, Depends, UploadFile, File, Request
from fastapi.security import OAuth2PasswordRequestForm

from app.config import settings
from app.exceptions import IncorrectEmailOrPasswordException, NotVerifyUser
from app.user.auth import AuthService
from app.user.dependencies import get_current_active_user, get_current_superuser
from app.user.models import User
from app.user.schemas import SUserCreate, SUserInfo, SToken, SUserUpdate
from app.user.services import UserService

router_auth = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)

router_user = APIRouter(
    prefix="/user",
    tags=["Пользователи"]
)


@router_auth.post("/register", status_code=status.HTTP_201_CREATED)
async def create_new_user(user: SUserCreate) -> SUserInfo:
    return await UserService.service_create_new_user(user)


@router_auth.post("/login")
async def login_user(
        response: Response, credentials: OAuth2PasswordRequestForm = Depends()
) -> SToken:
    user = await AuthService.authenticate_user(credentials.username, credentials.password)
    if not user:
        raise IncorrectEmailOrPasswordException

    if not user.is_verified:
        raise NotVerifyUser

    token = await AuthService.create_token(user.id)

    response.set_cookie(
        "access_token",
        token.access_token,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        httponly=True
    )
    response.set_cookie(
        "refresh_token",
        token.refresh_token,
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 30 * 24 * 60,
        httponly=True
    )

    return token


@router_auth.get("/verify-email")
async def get_verify_email(token: uuid.UUID):
    return await AuthService.verify_email(token)


@router_auth.post("/refresh")
async def refresh_token_user(request: Request, response: Response) -> SToken:
    new_token = await AuthService.refresh_token(request.cookies.get("refresh_token"))

    response.set_cookie(
        "access_token",
        new_token.access_token,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        httponly=True
    )
    response.set_cookie(
        "refresh_token",
        new_token.refresh_token,
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 30 * 24 * 60,
        httponly=True
    )
    return new_token


@router_auth.post("/logout")
async def logout_user(response: Response, request: Request, current_user: User = Depends(get_current_active_user)):
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")

    await AuthService.logout(request.cookies.get("refresh_token"))

    return {"authenticated": False}


@router_user.post("/upload-image", status_code=status.HTTP_201_CREATED)
async def upload_image_for_user(
        current_user: User = Depends(get_current_active_user),
        image: UploadFile = File(...)
):
    return await UserService.service_upload_image_for_user(current_user.id, image)


@router_user.put("/me")
async def update_user(user: SUserUpdate, current_user: User = Depends(get_current_active_user)) -> SUserInfo:
    return await UserService.service_update_user(current_user.id, user)


@router_user.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
        request: Request,
        response: Response,
        current_user: User = Depends(get_current_active_user)
):
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")

    await AuthService.logout(request.cookies.get("refresh_token"))
    await UserService.service_delete_user(current_user.id)

    return {"message": "Пользователь успешно удален"}


@router_user.get("")
async def get_users_list(current_superuser: User = Depends(get_current_superuser)) -> list[SUserInfo]:
    return await UserService.service_get_users_list()
