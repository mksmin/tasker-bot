# import libs
import logging

# import from libs
from contextlib import asynccontextmanager
from functools import wraps
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from typing import TypeVar, ParamSpec, Generic, Callable, Concatenate, Coroutine, Any, Type, AsyncGenerator

# import from modules
from database.db_helper import db_helper

# global
ModelType = TypeVar("ModelType")
P = ParamSpec("P")
R = TypeVar("R")
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
logger = logging.getLogger(__name__)


class BaseCRUDManager(Generic[ModelType]):
    def __init__(
            self,
            model: Type[ModelType],
            session_maker: Callable[[], AsyncGenerator[AsyncSession, None]],
    ):
        self.model = model
        self.session_maker = session_maker

    @staticmethod
    def _auto_session(
            func: Callable[
                Concatenate["BaseCRUDManager[ModelType]", P], Coroutine[Any, Any, R]
            ],
    ) -> Callable[Concatenate["BaseCRUDManager[ModelType]", P], Coroutine[Any, Any, R]]:
        @wraps(func)
        async def wrapper(self: "BaseCRUDManager[ModelType]", *args: P.args, **kwargs: P.kwargs) -> R:
            async with self.session_maker() as session:
                try:
                    kwargs["session"] = session
                    result = await func(self, *args, **kwargs)
                    await session.commit()
                    return result
                except Exception as e:
                    await session.rollback()
                    logger.exception("Error in session: %s", e)
                    raise

        return wrapper

    async def _create_one_entry(
            self,
            session: AsyncSession,
            instance: ModelType
    ) -> ModelType:
        session.add(instance)
        await session.flush()
        await session.refresh(instance)
        logger.info(f"Created {self.model.__name__} with id={instance.id}")
        return instance

    @_auto_session
    async def _create(self, *, session: AsyncSession, data: CreateSchemaType) -> ModelType:
        instance = self.model(**data.dict())
        return await self._create_one_entry(session=session, instance=instance)