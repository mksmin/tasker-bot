# import libs
import pytest

# import from libs
from datetime import datetime

# import from modules
from database.models import User, Task
from database.crud.managers import TaskManager, UserManager
from database.schemas import TaskReadSchema


@pytest.fixture
async def user_manager(db_session_maker) -> UserManager:
    return UserManager(session_maker=db_session_maker)


@pytest.fixture
async def task_manager(db_session_maker, user_manager) -> TaskManager:
    task_manager = TaskManager(session_maker=db_session_maker)
    task_manager.set_user_manager(user_manager)
    return task_manager


@pytest.fixture
async def created_user(user_manager: UserManager, user_data) -> User:
    return await user_manager.create_user(user_data=user_data)


@pytest.mark.asyncio
async def test_create_task(created_user: User, task_manager: TaskManager):
    task = await task_manager.create_task(
        user_tg=created_user.user_tg,
        task_text="Test task text"
    )

    assert isinstance(task, Task)
    assert task.text_task == "Test task text"
    assert task.is_done is False
    assert task.user_id == created_user.id
    assert isinstance(task.created_at, datetime)


@pytest.mark.asyncio
async def test_task_read_schema_from_orm(created_user: User, task_manager: TaskManager):
    task = await task_manager.create_task(
        user_tg=created_user.user_tg,
        task_text="Test task for schema"
    )

    schema = TaskReadSchema.model_validate(task)

    assert schema.id == task.id
    assert schema.text_task == task.text_task
    assert schema.is_done == task.is_done
    assert schema.user_id == task.user_id
    assert schema.created_at == task.created_at


@pytest.mark.asyncio
async def test_task_delete_logic(created_user: User, task_manager: TaskManager):
    task = await task_manager.create_task(
        user_tg=created_user.user_tg,
        task_text="Test task for delete"
    )

    assert task.is_done is False
    task.delete_task()
    assert task.is_done is True
