# import libs
import pytest

# import from libs
from datetime import datetime

# import from modules
from database.models import User, Task
from database.crud.managers import TaskManager, UserManager
from database.schemas import TaskReadSchema, UserReadSchema


@pytest.fixture
async def user_manager(db_session_maker) -> UserManager:
    return UserManager(session_maker=db_session_maker)


@pytest.fixture
async def task_manager(db_session_maker, user_manager) -> TaskManager:
    task_manager = TaskManager(session_maker=db_session_maker)
    task_manager.set_user_manager(user_manager)
    return task_manager


@pytest.fixture
async def created_user(user_manager: UserManager, user_data) -> UserReadSchema:
    return await user_manager.create_user(user_data=user_data)


@pytest.mark.asyncio
async def test_create_task(created_user: User, task_manager: TaskManager):
    task = await task_manager.create_task(
        user_tg=created_user.user_tg, task_text="Test task text"
    )

    assert isinstance(task, TaskReadSchema)
    assert task.text_task == "Test task text"
    assert task.is_done is False
    assert task.user_id == created_user.id
    assert isinstance(task.created_at, datetime)


@pytest.mark.asyncio
async def test_get_task(created_user: User, task_manager: TaskManager):
    task = await task_manager.create_task(
        user_tg=created_user.user_tg, task_text=f"Test get task by id"
    )

    result = await task_manager.get_task_by_id(task_id=task.id)
    assert isinstance(result, TaskReadSchema)
    assert result.id == task.id
    assert result.text_task == task.text_task
    assert result.is_done is False
    assert result.user_id == created_user.id
    assert isinstance(result.created_at, datetime)


@pytest.mark.asyncio
async def test_get_task_invalid_id(task_manager: TaskManager):
    with pytest.raises(ValueError):
        await task_manager.get_task_by_id(task_id=12345)


@pytest.mark.asyncio
async def test_get_paginated_tasks_with_pagination(
    created_user: User, task_manager: TaskManager
):
    for i in range(10):
        await task_manager.create_task(
            user_tg=created_user.user_tg, task_text=f"Test task #{i}"
        )

    # Page 1: offset=0, limit=5
    tasks_page_1 = await task_manager.get_paginated_tasks(
        user_tg=created_user.user_tg,
        offset=0,
        limit=5,
    )

    assert len(tasks_page_1) == 5
    tasks_ids_page_1 = [task.id for task in tasks_page_1]
    assert tasks_ids_page_1 == sorted(tasks_ids_page_1, reverse=True)

    # Page 2: offset=5, limit=5
    tasks_page_2 = await task_manager.get_paginated_tasks(
        user_tg=created_user.user_tg,
        offset=5,
        limit=5,
    )

    assert len(tasks_page_2) == 5
    tasks_ids_page_2 = [task.id for task in tasks_page_2]
    assert tasks_ids_page_2 == sorted(tasks_ids_page_2, reverse=True)


@pytest.mark.asyncio
async def test_get_paginated_tasks_with_limit_exceeding_available(
    created_user: User, task_manager: TaskManager
):
    for i in range(3):
        await task_manager.create_task(
            user_tg=created_user.user_tg, task_text=f"Test task #{i}"
        )

    tasks = await task_manager.get_paginated_tasks(
        user_tg=created_user.user_tg,
        offset=0,
        limit=5,
    )
    assert len(tasks) == 3
    assert all(task.user_id == created_user.id for task in tasks)


@pytest.mark.asyncio
async def test_get_paginated_tasks_no_tasks(
    created_user: User, task_manager: TaskManager
):
    tasks = await task_manager.get_paginated_tasks(
        user_tg=created_user.user_tg,
        offset=0,
        limit=5,
    )
    assert tasks == []
    assert isinstance(tasks, list)


@pytest.mark.asyncio
async def test_get_paginated_tasks_ordering(
    created_user: User, task_manager: TaskManager
):
    for i in range(3):
        await task_manager.create_task(
            user_tg=created_user.user_tg, task_text=f"Test task #{i}"
        )

    tasks = await task_manager.get_paginated_tasks(
        user_tg=created_user.user_tg,
        offset=0,
        limit=5,
    )
    assert [task.id for task in tasks] == [3, 2, 1]


@pytest.mark.asyncio
async def test_task_mark_as_done(created_user: User, task_manager: TaskManager):
    task = await task_manager.create_task(
        user_tg=created_user.user_tg, task_text=f"Test task to mark as done"
    )

    assert task.is_done is False

    result = await task_manager.mark_as_done(task_id=task.id)
    assert result is True

    updated_task = await task_manager.get_task_by_id(task_id=task.id)
    assert updated_task.is_done is True
    assert updated_task.user_id == created_user.id
    assert updated_task.text_task == "Test task to mark as done"


@pytest.mark.asyncio
async def test_mark_as_done_invalid_task(task_manager: TaskManager):
    result = await task_manager.mark_as_done(task_id=12345)
    assert result is False


@pytest.mark.asyncio
async def test_mark_as_done_already_done(created_user: User, task_manager: TaskManager):
    task = await task_manager.create_task(
        user_tg=created_user.user_tg, task_text=f"Already done task"
    )

    await task_manager.mark_as_done(task_id=task.id)

    result = await task_manager.mark_as_done(task_id=task.id)
    assert result is False


@pytest.mark.asyncio
async def test_task_read_schema_from_orm(created_user: User, task_manager: TaskManager):
    task = await task_manager.create_task(
        user_tg=created_user.user_tg, task_text="Test task for schema"
    )

    schema = TaskReadSchema.model_validate(task)

    assert schema.id == task.id
    assert schema.text_task == task.text_task
    assert schema.is_done == task.is_done
    assert schema.user_id == task.user_id
    assert schema.created_at == task.created_at


@pytest.mark.asyncio
async def test_get_random_tasks_returns_correct_count(
    created_user: User, task_manager: TaskManager
):
    for i in range(5):
        await task_manager.create_task(
            user_tg=created_user.user_tg, task_text=f"Test task #{i}"
        )

    tasks = await task_manager.get_random_tasks(user_tg=created_user.user_tg, count=5)

    assert isinstance(tasks, list)
    assert len(tasks) == 5
    for task in tasks:
        assert isinstance(task, TaskReadSchema)
        assert task.user_id == created_user.id
        assert task.is_done is False


@pytest.mark.asyncio
async def test_get_random_tasks_does_not_return_done(
    created_user: User, task_manager: TaskManager
):
    for i in range(5):
        await task_manager.create_task(
            user_tg=created_user.user_tg, task_text=f"Test task #{i}"
        )

    tasks = await task_manager.get_random_tasks(user_tg=created_user.user_tg, count=5)
    for task in tasks:
        await task_manager.mark_as_done(task_id=task.id)

    tasks = await task_manager.get_random_tasks(user_tg=created_user.user_tg, count=5)
    assert isinstance(tasks, list)
    assert len(tasks) == 0
    assert tasks == []


@pytest.mark.asyncio
async def test_get_random_tasks_empty_result(
    created_user: User, task_manager: TaskManager
):
    tasks = await task_manager.get_random_tasks(user_tg=created_user.user_tg, count=3)
    assert tasks == []
