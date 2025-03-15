# import from lib
from functools import wraps
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

# import from modules
from database import async_session, User, Task
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
        async with async_session() as session:
            print(locals())
            return await function(session, *args, **kwargs)

    return wrapper


@connection
async def get_user_by_tgid(session: AsyncSession, tgid: int) -> User:
    user = await session.scalar(
        select(User).where(User.user_tg == tgid)
    )

    if not user:
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
