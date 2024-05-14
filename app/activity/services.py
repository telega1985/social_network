from app.activity.schemas import SActivity
from app.database import async_session_maker

from app.activity.dao import ActivityDAO


class ActivityService:
    @classmethod
    async def service_get_activities_by_username(
            cls, username: str, page: int = 1, limit: int = 10
    ) -> list[SActivity]:
        """
        Получить активность пользователя по имени пользователя
        """
        offset = (page - 1) * limit

        async with async_session_maker() as session:
            return await ActivityDAO.db_get_activities_by_username(session, username, offset, limit)
