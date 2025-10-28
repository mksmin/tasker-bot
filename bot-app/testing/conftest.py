from collections.abc import AsyncGenerator
from typing import Any
from unittest.mock import AsyncMock

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from crud.crud_service import CRUDService
from crud.managers import BaseCRUDManager
from database.models import Base, User
from database.schemas import UserCreateSchema


@pytest.fixture(scope="function")
def anyio_backend() -> str:
    return "asyncio"


@pytest_asyncio.fixture(scope="function")
async def db_engine() -> AsyncGenerator[AsyncEngine, None]:
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session_maker(db_engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(bind=db_engine, expire_on_commit=False)


@pytest_asyncio.fixture
async def db_session(
    db_session_maker: async_sessionmaker[AsyncSession],
) -> AsyncGenerator[AsyncSession, None]:
    async with db_session_maker() as session:
        yield session


@pytest.fixture
def user_data() -> dict[str, Any]:
    return {
        "user_tg": 999,
        "first_name": "Max",
        "last_name": "Test",
        "username": "test_user",
    }


@pytest.fixture
def user_schema(user_data: dict[str, Any]) -> UserCreateSchema:
    return UserCreateSchema(**user_data)


@pytest.fixture
async def mock_session() -> AsyncSession:
    return AsyncMock(spec=AsyncSession)


@pytest.fixture
async def mock_crud_service(
    mock_session: AsyncSession,
) -> CRUDService:
    return CRUDService(mock_session)


@pytest.fixture
async def instance(
    mock_session: AsyncSession,
) -> BaseCRUDManager[User]:
    return BaseCRUDManager[User](
        model=User,
        session=mock_session,
    )


@pytest.fixture
async def created_user(
    user_schema: UserCreateSchema,
) -> User:
    return User(**user_schema.model_dump())
