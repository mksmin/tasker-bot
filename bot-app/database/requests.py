# import from lib
from functools import wraps
from typing import Optional, Any, TypeVar, Callable, Awaitable, Coroutine

from sqlalchemy import select, func, false
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

# import from modules
from database import (  # type: ignore
    User,
    Task,
    UserSettings,
    SettingsRepo,
    db_helper,
)
from config import logger


T = TypeVar("T")


def connection(
    function: Callable[..., Awaitable[T]],
) -> Callable[..., Awaitable[T]]:
    """
    Decorator function that wraps the provided function with a database session.

    Args:
        function: The function to be wrapped.

    Returns:
        The wrapped function.
    """

    @wraps(function)
    async def wrapper(*args: Any, **kwargs: Any) -> T:
        """
        Asynchronous wrapper function that creates a database session and passes it to the wrapped function.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            The result of the wrapped function.
        """
        async for session in db_helper.session_getter():  # type: ignore
            return await function(session, *args, **kwargs)

        raise RuntimeError("No database session available")  # for fix mypy error

    return wrapper


@connection
async def get_user_by_tgid(
    session: AsyncSession,
    tgid: int,
    user_data: Optional[dict[str, Any]] = None,
) -> User:
    user = await session.scalar(select(User).where(User.user_tg == tgid))

    if user_data and user:
        for key, value in user_data.items():
            setattr(user, key, value)
        session.add(user)
        await session.commit()
        await session.refresh(user)

    if not user:
        if user_data:
            user = User(user_tg=tgid, **user_data)
        else:
            user = User(user_tg=tgid)
        session.add(user)
        await session.commit()
        await session.refresh(user)

    return user


@connection
async def get_list_of_random_tasks(
    session: AsyncSession, user_tg: int, count: int = 5
) -> Any:
    user = await get_user_by_tgid(tgid=user_tg)
    tasks = await session.scalars(
        select(Task)
        .where(Task.user_id == user.id, Task.is_done == False)
        .order_by(func.random())
        .limit(count)
    )

    return tasks


@connection
async def get_user_settings(session: AsyncSession, user_tg: int) -> Any:
    user = await get_user_by_tgid(tgid=user_tg)
    settings = await session.scalar(
        select(UserSettings).where(UserSettings.user_id == user.id)
    )
    if not settings:
        new_settings = SettingsRepo(session)
        await new_settings.set(user.id)
        settings = await new_settings.get(user.id)

    return settings


@connection
async def get_list_of_all_tasks(
    session: AsyncSession,
    user_tg: int,
    user_data: Optional[dict[str, Any]] = None,
) -> Any:
    try:
        user = await get_user_by_tgid(tgid=user_tg, user_data=user_data)
        tasks = await session.scalars(
            select(Task).where(Task.user_id == user.id, Task.is_done == False)
        )
    except Exception as e:
        logger.error("Error get list of tasks: ", e)
        raise Exception(f"Error get list of tasks: {e}")
    return tasks


@connection
async def get_user_relationship(session: AsyncSession, user_tg: int) -> Any:
    user = await get_user_by_tgid(tgid=user_tg)
    # user = await session.get(User, user.id,  options=[selectinload(User.settings)])
    user = await session.get(User, user.id)  # type: ignore
    await session.refresh(user, attribute_names=["settings"])

    return user


@connection
async def finish_task(session: AsyncSession, task: Task) -> bool:
    new_task = await session.scalar(select(Task).where(Task.id == task.id))

    if not new_task:
        return False

    new_task.delete_task()

    session.add(new_task)
    await session.commit()

    return True
