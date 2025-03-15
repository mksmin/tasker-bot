# import lib
import asyncio

# import from lib
from datetime import datetime
from dotenv import load_dotenv
from pathlib import Path
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine

# import from modules
from config.config import get_token, logger



logger.info(f'Start bot: {get_token("POSTGRES_URL")}')

postgres_token = get_token('POSTGRES_URL')
logger.info(f'postgresql token {postgres_token}')

engine = create_async_engine(
    url='postgresql+asyncpg://postgres:86Unsq1072@localhost/tasksdb',
    echo=False
)
async_session = async_sessionmaker(
    bind=engine,
    expire_on_commit=True
)


class Base(AsyncAttrs, DeclarativeBase):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)


class TimeStampMixin:
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, nullable=True)


async def start_engine():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
