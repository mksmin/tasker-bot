from contextlib import asynccontextmanager

import pytest
import asyncio

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import clear_mappers

from database.models import Base, User
from database.schemas import UserCreateSchema
from database.crud.managers.base import BaseCRUDManager
from database import db_helper


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="session")
async def db_engine():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest.fixture
async def db_session(db_engine):
    async_session = async_sessionmaker(
        bind=db_engine,
        expire_on_commit=False
    )
    async with async_session() as session:
        yield session


def fake_session_maker(session: AsyncSession):
    @asynccontextmanager
    async def getter():
        yield session

    return getter


@pytest.mark.asyncio
async def test_create_user(db_session):

    async for session in db_session:
        user_crud = BaseCRUDManager[User, UserCreateSchema](
            model=User,
            session_maker=fake_session_maker(session)
        )

        user_data = UserCreateSchema(
            user_tg=123456789,
            first_name="John",
        )

        created = await user_crud.create(session=, data=user_data)

        assert isinstance(created, User)
        assert created.id is not None
        assert created.created_at is not None
        assert created.first_name == "John"
        assert created.user_tg == 123456789

        break
