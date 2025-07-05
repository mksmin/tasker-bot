# import libs
import pytest

# import from libs
from aiogram.types import Message, User
from aiogram.fsm.context import FSMContext
from datetime import time
from unittest.mock import AsyncMock, patch, MagicMock

# import from modules
import database.requests as rq

from app.handlers import cmd_start, cmd_daily_tasks
from app import keyboards as kb
from database.models import UserSettings, Task
from database.requests import get_user_by_tgid


@pytest.fixture
async def mock_message():
    message = MagicMock(spec=Message)
    message.from_user = User(
        id=123456,
        first_name="John",
        last_name="Doe",
        username="johndoe",
        is_bot=False,
        language_code='ru'
    )
    return message


@pytest.mark.asyncio
async def test_cmd_start(mock_message):
    mock_message.answer = AsyncMock()

    with patch('database.requests.get_user_by_tgid', new_callable=AsyncMock) as mock_get_user_by_tgid:
        await cmd_start(mock_message)

        mock_get_user_by_tgid.assert_awaited_once_with(
            123456,
            user_data={"first_name": "John",
                       "last_name": "Doe",
                       "username": "johndoe"}
        )
        mock_message.answer.assert_awaited_once_with(
            "Привет! Добавляй афоризмы, а я буду каждый день присылать тебе 5 случайных! "
        )


@pytest.mark.asyncio
async def test_cmd_daily_tasks_no_tasks(mock_message):
    mock_message.answer = AsyncMock()

    mock_settings = UserSettings(
        id=1,
        user_id=mock_message.from_user.id,
        count_tasks=5,
        send_time=time(9, 0)
    )

    with (
        patch.object(
            rq, 'get_user_settings',
            new_callable=AsyncMock,
            return_value=mock_settings

        ) as mock_get_user_settings,
        patch.object(
            rq, 'get_list_of_random_tasks',
            new_callable=AsyncMock,
            return_value=[]
        ) as mock_get_list_of_random_tasks
    ):
        await cmd_daily_tasks(mock_message)

        mock_get_user_settings.assert_awaited_once_with(
            user_tg=123456
        )
        mock_get_list_of_random_tasks.assert_awaited_once_with(
            user_tg=123456,
            count=5
        )
        mock_message.answer.assert_awaited_once_with(
            "У тебя нет сохраненных текстов"
        )


@pytest.mark.asyncio
async def test_cmd_daily_tasks_with_tasks(mock_message):
    test_tasks = [
        Task(text_task="Test task 1"),
        Task(text_task="Test task 2"),
        Task(text_task="Task 3")
    ]

    expected_task_count = 3
    expected_message = (
        "Доброе утро, вот твои аффирмации на сегодня:\n\n"
        "1. Test task 1\n"
        "2. Test task 2\n"
        "3. Task 3"
    )

    mock_message.answer = AsyncMock()
    mock_settings = UserSettings(
        id=1,
        user_id=mock_message.from_user.id,
        count_tasks=expected_task_count,
        send_time=time(10, 0)
    )

    with (
        patch.object(
            rq, 'get_user_settings',
            new_callable=AsyncMock,
            return_value=mock_settings

        ) as mock_get_user_settings,
        patch.object(
            rq, 'get_list_of_random_tasks',
            new_callable=AsyncMock,
            return_value=test_tasks
        ) as mock_get_list_of_random_tasks
    ):
        await cmd_daily_tasks(mock_message)
        mock_message.answer.assert_awaited_once_with(
            text=expected_message,
            reply_markup=kb.finishing_task
        )
