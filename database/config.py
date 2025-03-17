# import lib
import asyncio

# import from lib
# from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine

# import from modules
from config.config import get_token, logger

postgres_token = get_token('POSTGRES_URL')
logger.info(f'postgresql token {postgres_token}')

engine = create_async_engine(
    url=postgres_token,
    echo=False
)
async_session = async_sessionmaker(
    bind=engine,
    expire_on_commit=True
)


async def start_engine():
    pass
