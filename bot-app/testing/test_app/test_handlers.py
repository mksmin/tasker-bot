"""
Модуль с тестами для обработчиков команд бота

Проверяю логику работы обработчиков без обращения к БД,
а только итоговое форматирование и ответы и логику работы
функций с полученными от БД объектами
"""

from collections.abc import AsyncGenerator
from datetime import time
from typing import cast
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from aiogram.types import Message, User

# import from modules
import database.requests as rq
from bot.handlers import cmd_daily_tasks, cmd_start
from database.crud import crud_manager
from database.models import Task, UserSettings


@pytest.fixture
async def mock_message() -> AsyncGenerator[Message, None]:
    """
    Fixture that returns a mocked Message object with a fake user.
    """
    message = MagicMock(spec=Message)
    message.from_user = User(
        id=123456,
        first_name="John",
        last_name="Doe",
        username="johndoe",
        is_bot=False,
        language_code="ru",
    )
    yield message


@pytest.mark.asyncio
async def test_cmd_start(mock_message: Message) -> None:
    """
    Test that the /start command registers the user and sends a welcome message
    """
    mock_message.answer = AsyncMock()  # type: ignore[method-assign]

    with (
        patch.object(
            crud_manager.user,
            "create_user",
            new_callable=AsyncMock,
        ) as mock_create_user,
        patch.object(
            rq,
            "get_user_settings",
            new_callable=AsyncMock,
        ) as mock_get_user_settings,
    ):
        mock_user = AsyncMock()
        mock_user.user_tg = 123456
        mock_create_user.return_value = mock_user

        await cmd_start(
            mock_message,
            from_user=mock_message.from_user,
        )
        mock_create_user.assert_awaited_once_with(
            user_data={
                "user_tg": 123456,
                "first_name": "John",
                "last_name": "Doe",
                "username": "johndoe",
            },
        )
        mock_message.answer.assert_awaited_once_with(
            "Привет! \n\n"
            "Отправь мне любые афоризмы <i>(по одной шт за раз)</i>, "
            "а я буду каждый день присылать тебе 5 случайных! \n\n"
            "Обычно я отправляю в 9 утра по Москве. Используй команду /settings, "
            "чтобы изменить время отправки",
        )

        mock_get_user_settings.assert_awaited_once_with(user_tg=123456)


@pytest.mark.asyncio
async def test_cmd_daily_tasks_no_tasks(mock_message: Message) -> None:
    """
    Test that the /daily command sends a message when no tasks are available
    """
    from_user = cast(User, mock_message.from_user)
    mock_message.answer = AsyncMock()  # type: ignore[method-assign]

    mock_settings = UserSettings(
        id=1,
        user_id=from_user.id,
        count_tasks=5,
        send_time=time(9, 0),
    )

    with (
        patch.object(
            rq,
            "get_user_settings",
            new_callable=AsyncMock,
            return_value=mock_settings,
        ) as mock_get_user_settings,
        patch.object(
            crud_manager.task,
            "get_random_tasks",
            new_callable=AsyncMock,
            return_value=[],
        ) as mock_get_list_of_random_tasks,
    ):
        await cmd_daily_tasks(
            mock_message,
            from_user=mock_message.from_user,
        )

        mock_get_user_settings.assert_awaited_once_with(user_tg=123456)
        mock_get_list_of_random_tasks.assert_awaited_once_with(user_tg=123456, count=5)
        mock_message.answer.assert_awaited_once_with("У тебя нет сохраненных текстов")


@pytest.mark.asyncio
async def test_cmd_daily_tasks_with_tasks(mock_message: Message) -> None:
    """
    Test that the /daily command sends a list of tasks when available
    """
    from_user = cast(User, mock_message.from_user)
    test_tasks = [
        Task(text_task="Test task 1"),
        Task(text_task="Test task 2"),
        Task(text_task="Task 3"),
    ]

    expected_task_count = 3
    expected_message = (
        "Доброе утро, вот твои аффирмации на сегодня:\n\n"
        "1. Test task 1\n"
        "2. Test task 2\n"
        "3. Task 3"
    )

    mock_message.answer = AsyncMock()  # type: ignore[method-assign]
    mock_settings = UserSettings(
        id=1,
        user_id=from_user.id,
        count_tasks=expected_task_count,
        send_time=time(10, 0),
    )

    with (
        patch.object(
            rq,
            "get_user_settings",
            new_callable=AsyncMock,
            return_value=mock_settings,
        ) as mock_get_user_settings,  # noqa: F841
        patch.object(
            crud_manager.task,
            "get_random_tasks",
            new_callable=AsyncMock,
            return_value=test_tasks,
        ) as mock_get_list_of_random_tasks,
    ):
        await cmd_daily_tasks(
            mock_message,
            from_user=mock_message.from_user,
        )
        mock_get_list_of_random_tasks.assert_awaited_once_with(
            user_tg=123456,
            count=expected_task_count,
        )
        mock_message.answer.assert_awaited_once_with(
            text=expected_message,
        )
