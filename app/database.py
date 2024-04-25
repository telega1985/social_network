from typing import Annotated
from datetime import datetime

from sqlalchemy import func, TIMESTAMP
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, mapped_column

from app.config import settings


DATABASE_URL = settings.DATABASE_URL

engine = create_async_engine(DATABASE_URL)

async_session_maker = async_sessionmaker(engine, expire_on_commit=False)

intpk = Annotated[int, mapped_column(primary_key=True, index=True)]

created_at = Annotated[datetime, mapped_column(TIMESTAMP(timezone=True), server_default=func.now())]


class Base(DeclarativeBase):
    pass
