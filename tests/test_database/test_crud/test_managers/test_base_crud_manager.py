# import libs
import pytest

# import from libs
from datetime import datetime
from pydantic import ValidationError

# import from modules
from database.models import User
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
