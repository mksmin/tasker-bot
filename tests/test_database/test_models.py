# import libs
import pytest

# import from libs
from datetime import datetime, time

# import from modules
from database import models as md


@pytest.fixture
async def user(db_session):
    user = md.User(
        user_tg=999,
        first_name="Max",
        last_name="Testovich",
        username="test_user"
    )
    db_session.add(user)
    await db_session.flush()
    return user


@pytest.mark.asyncio
async def test_user_model_create(user, db_session):
    await db_session.refresh(user)

    assert user.id is not None
    assert isinstance(user.created_at, datetime)
    assert user.username == "test_user"
    assert user.last_name == "Testovich"
    assert user.first_name == "Max"
    assert user.user_tg == 999


@pytest.mark.asyncio
async def test_task_model_create(user, db_session):
    new_task = md.Task(
        text_task="Do the test",
        user_id=user.id
    )
    db_session.add(new_task)
    await db_session.commit()

    await db_session.refresh(new_task)
    await db_session.refresh(user, attribute_names=["tasks"])

    assert new_task.id is not None
    assert new_task.user_id == user.id
    assert new_task.text_task == "Do the test"
    assert new_task.is_done is False
    assert isinstance(new_task.created_at, datetime)

    assert user.tasks[0].id == new_task.id


@pytest.mark.asyncio
async def test_task_delete_logic(user, db_session):
    task = md.Task(text_task="Do the test", user_id=user.id)
    db_session.add(task)

    await db_session.commit()
    await db_session.refresh(task)

    assert task.is_done is False

    task.delete_task()
    assert task.is_done is True

    db_session.add(task)
    await db_session.commit()
    await db_session.refresh(task)

    assert task.is_done is True


@pytest.mark.asyncio
async def test_user_settings_create(user, db_session):
    settings = md.UserSettings(
        user_id=user.id,
        count_tasks=10,
        send_time=time(9, 0)
    )
    db_session.add(settings)
    await db_session.commit()
    await db_session.refresh(settings)

    assert settings.id is not None
    assert settings.user_id == user.id
    assert settings.count_tasks == 10
    assert settings.send_time == time(9, 0)


@pytest.mark.asyncio
async def test_user_settings_relationship(user, db_session):
    settings = md.UserSettings(
        user_id=user.id,
        count_tasks=10,
        send_time=time(9, 0)
    )
    db_session.add(settings)
    await db_session.commit()

    await db_session.refresh(user, attribute_names=["settings"])

    assert user.settings is not None
    assert user.settings.id == settings.id
    assert user.settings.count_tasks == 10
    assert user.settings.send_time == time(9, 0)
    assert settings.user.id == user.id
