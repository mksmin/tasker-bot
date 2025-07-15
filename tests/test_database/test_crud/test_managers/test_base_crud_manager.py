# import libs
import pytest

# import from libs
from datetime import datetime
from pydantic import ValidationError

# import from modules
from database.models import User
from database.schemas import UserCreateSchema
from database.crud.managers.base import BaseCRUDManager


@pytest.fixture
async def instance(db_session_maker) -> BaseCRUDManager:
    user_crud = BaseCRUDManager[User](
        model=User,
        session_maker=db_session_maker
    )
    return user_crud


@pytest.fixture
async def created_user(user_schema, instance) -> User:
    return await instance.create(data=user_schema)


@pytest.mark.asyncio
async def test_create_user(created_user: User) -> None:
    created = created_user

    assert isinstance(created, User)
    assert created.id is not None
    assert isinstance(created.created_at, datetime)
    assert created.user_tg == 999
    assert created.first_name == "Max"
    assert created.last_name == "Test"
    assert created.username == "test_user"


def test_create_user_missing_fields(instance):
    with pytest.raises(ValidationError):
        UserCreateSchema(**{})


@pytest.mark.asyncio
async def test_exists_user(created_user: User, instance: BaseCRUDManager[User]) -> None:
    user = created_user
    exists = await instance.exist(
        field="id", value=user.id
    )

    assert exists is not None


@pytest.mark.asyncio
async def test_get_one_user(created_user: User, instance: BaseCRUDManager[User]) -> None:
    get_user = await instance.get(
        user_tg=created_user.user_tg
    )
    assert get_user is not None
    assert get_user.id == created_user.id
