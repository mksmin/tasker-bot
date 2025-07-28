import logging
from functools import wraps

from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from typing import (
    Any,
    Callable,
    Concatenate,
    Coroutine,
    ParamSpec,
    TYPE_CHECKING,
    TypeVar,
)

from database.db_helper import db_helper

if TYPE_CHECKING:
    from app.core.database.crud.repositories import BaseRepository

# globals
ModelType = TypeVar("ModelType")
P = ParamSpec("P")
R = TypeVar("R")
log = logging.getLogger(__name__)


class SessionManager:
    def __init__(
            self,
            session_maker: async_sessionmaker[AsyncSession],
    ):
        self.session_maker = session_maker

    def __call__(self,
                 func: Callable[
                     Concatenate["BaseRepository[ModelType]", P], Coroutine[Any, Any, R]
                 ],
                 ) -> Callable[
        Concatenate["BaseRepository[ModelType]", P], Coroutine[Any, Any, R]
    ]:
        @wraps(func)
        async def wrapper(
                self_obj: "BaseRepository[ModelType]",
                *args: P.args,
                **kwargs: P.kwargs,
        ) -> R:
            async with self.session_maker() as session:
                try:
                    kwargs["session"] = session
                    result = await func(self_obj, *args, **kwargs)
                    await session.commit()
                    return result
                except Exception as e:
                    await session.rollback()
                    log.error("Error in session_getter", exc_info=True)
                    raise

        return wrapper


auto_session = SessionManager(
    session_maker=db_helper.session_factory
)