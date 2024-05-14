from sqlalchemy import select, insert, delete, update
from sqlalchemy.ext.asyncio import AsyncSession

from typing import Any, Dict, List


class BaseDAO:
    model = None

    @classmethod
    async def find_one_or_none(cls, session: AsyncSession, **filter_by):
        query = select(cls.model).filter_by(**filter_by)
        result = await session.execute(query)
        return result.scalars().one_or_none()

    @classmethod
    async def find_all(cls, session: AsyncSession):
        query = select(cls.model)
        result = await session.execute(query)
        return result.scalars().all()

    @classmethod
    async def find_all_filter_by(cls, session: AsyncSession, **filter_by):
        query = select(cls.model).filter_by(**filter_by)
        result = await session.execute(query)
        return result.scalars().all()

    @classmethod
    async def add(cls, session: AsyncSession, **data):
        query = insert(cls.model).values(**data).returning(cls.model)
        result = await session.execute(query)
        return result.scalars().one()

    @classmethod
    async def update(cls, session: AsyncSession, *where, **data):
        query = update(cls.model).where(*where).values(**data).returning(cls.model)
        result = await session.execute(query)
        return result.scalars().one()

    @classmethod
    async def delete(cls, session: AsyncSession, **filter_by):
        query = delete(cls.model).filter_by(**filter_by)
        await session.execute(query)

    @classmethod
    async def add_many(cls, session: AsyncSession, data: List[Dict[str, Any]]):
        """
        Добавляет множество записей
        """
        query = insert(cls.model).returning(cls.model)
        result = await session.execute(query, data)

        return result.scalars().all()
