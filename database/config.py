from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

# import from modules
from config.config import get_token, logger, settings

postgres_token = get_token('POSTGRES_URL')

engine = create_async_engine(
    url=str(settings.db.url),
    echo=False
)
async_session = async_sessionmaker(
    bind=engine,
    expire_on_commit=True
)


async def start_engine():
    pass
