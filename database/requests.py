# import from lib
from functools import wraps
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

# import from modules
from database import User, Task, db_helper
from config import logger


def connection(function):
    """
    Decorator function that wraps the provided function with a database session.

    Args:
        function: The function to be wrapped.

    Returns:
        The wrapped function.
    """

    @wraps(function)
    async def wrapper(*args, **kwargs):
        """
        Asynchronous wrapper function that creates a database session and passes it to the wrapped function.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            The result of the wrapped function.
        """
        async for session in db_helper.session_getter():
            return await function(session, *args, **kwargs)

    return wrapper


@connection
async def get_user_by_tgid(session: AsyncSession, tgid: int, user_data: dict = None) -> User:
    user = await session.scalar(
        select(User).where(User.user_tg == tgid)
    )

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
async def add_task(session: AsyncSession, user_tg: int, user_text: str) -> bool:
    user = await get_user_by_tgid(user_tg)

    task = Task(
        text_task=user_text,
        user_id=user.id
    )
    try:
        session.add(task)
        await session.commit()
        return True

    except Exception as e:
        logger.error("Error add task: ", e)
        return False


@connection
async def get_list_of_random_tasks(session: AsyncSession, used_tg: int, count: int = 5) -> any:
    user = await get_user_by_tgid(tgid=used_tg)
    tasks = await session.scalars(
        select(Task).where(
            Task.user_id == user.id,
            Task.is_done == False
        ).order_by(func.random()).limit(count)
    )

    return tasks


@connection
async def get_list_of_all_tasks(session: AsyncSession, user_tg: int) -> any:
    try:
        user = await get_user_by_tgid(tgid=user_tg)
        tasks = await session.scalars(
            select(Task).where(Task.user_id == user.id,
                               Task.is_done == False)
        )
    except Exception as e:
        logger.error("Error get list of tasks: ", e)
        raise Exception(f"Error get list of tasks: {e}")
    return tasks


@connection
async def finish_task(session: AsyncSession, task: Task) -> bool:
    new_task = await session.scalar(
        select(Task).where(Task.id == task.id)
    )

    new_task.delete_task()

    if new_task.is_done:
        session.add(new_task)
        await session.commit()
        return True
