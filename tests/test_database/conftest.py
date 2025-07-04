# import libs
import pytest
import pytest_asyncio

# import from libs
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

# import from modules
from database.models import Base


@pytest.fixture(scope="function")
def anyio_backend():
    return "asyncio"


@pytest_asyncio.fixture(scope="function")
async def db_engine():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session_maker(db_engine):
    return async_sessionmaker(bind=db_engine, expire_on_commit=False)


@pytest_asyncio.fixture
async def db_session(db_session_maker):
    async with db_session_maker() as session:
        yield session
