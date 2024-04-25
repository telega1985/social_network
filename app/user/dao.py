from app.dao.base import BaseDAO
from app.user.models import User, RefreshSession, VerificationSession


class UserDAO(BaseDAO):
    model = User


class RefreshSessionDAO(BaseDAO):
    model = RefreshSession


class VerificationSessionDAO(BaseDAO):
    model = VerificationSession
