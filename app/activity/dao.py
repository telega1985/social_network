from app.dao.base import BaseDAO
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.activity.models import Activity


class ActivityDAO(BaseDAO):
    model = Activity

    @classmethod
    async def db_get_activities_by_username(cls, session: AsyncSession, username: str, offset: int, limit: int = 10):
        query = (
            select(cls.model)
            .filter_by(username=username)
            .order_by(cls.model.timestamp.desc())
            .offset(offset).limit(limit)
        )
        result = await session.execute(query)
        return result.scalars().all()
