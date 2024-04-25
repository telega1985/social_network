from sqlalchemy import select, insert, delete, update
from sqlalchemy.ext.asyncio import AsyncSession


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
    async def add_many(cls, session: AsyncSession, data: list[dict[str, int]], return_ids: bool = False):
        """
        Добавляет множество записей
        """
        query = insert(cls.model).values(data)

        if return_ids:
            query = query.returning(cls.model.id)
            result = await session.execute(query, data)
            return result.scalars().all()

        await session.execute(query)
