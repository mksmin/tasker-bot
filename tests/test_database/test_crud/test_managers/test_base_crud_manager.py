from contextlib import asynccontextmanager
from datetime import datetime

import pytest
import pytest_asyncio
import asyncio

from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from database.models import Base, User
from database.schemas import UserCreateSchema
from database.crud.managers.base import BaseCRUDManager


@pytest.mark.asyncio
async def test_create_user(db_session_maker):
    user_crud = BaseCRUDManager[User](
        model=User,
        session_maker=db_session_maker
    )

    user_data = UserCreateSchema(
        user_tg=123456789,
        first_name="John",
    )

    created = await user_crud.create(data=user_data)

    assert isinstance(created, User)
    assert created.id is not None
    assert isinstance(created.created_at, datetime)
    assert created.first_name == "John"
    assert created.user_tg == 123456789


@pytest.mark.asyncio
async def test_create_user_missing_fields(db_session_maker):
    user_crud = BaseCRUDManager[User](
        model=User,
        session_maker=db_session_maker
    )

    with pytest.raises(ValidationError):
        invalid_data = UserCreateSchema(**{})
        await user_crud.create(data=invalid_data)
