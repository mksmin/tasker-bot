# import libs
import pytest

# import from modules
from database.models import User
from database.crud import crud_manager
from database.crud.managers import UserManager


@pytest.fixture
async def user_manager(db_session_maker) -> UserManager:
    crud_manager.user.session_maker = db_session_maker
    yield crud_manager.user


@pytest.mark.asyncio
async def test_create_user_new(user_data, user_manager: UserManager):
    user = await user_manager.create_user(user_data)

    assert user is not None
    assert isinstance(user, User)
    assert user.first_name == user_data['first_name']
    assert user.last_name == user_data['last_name']
    assert user.username == user_data['username']


@pytest.mark.asyncio
async def test_create_user_existing(user_data, user_manager: UserManager, created_user):
    user_data.update({
        'first_name': 'John',
        'last_name': 'Doe',
        'username': 'johndoe',
    })

    user = await user_manager.create_user(user_data)

    assert user.id == created_user.id
    assert user.first_name == created_user.first_name
    assert user.last_name == created_user.last_name
    assert user.username == created_user.username
