# import libs
import logging

# import from libs
from contextlib import asynccontextmanager
from functools import wraps
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from typing import TypeVar, ParamSpec, Generic, Callable, Concatenate, Coroutine, Any, Type, AsyncGenerator

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
            session_maker: async_sessionmaker[AsyncSession],
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
        async def wrapper(
                self: "BaseCRUDManager[ModelType]",
                *args: P.args,
                **kwargs: P.kwargs,
        ) -> R:
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

    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        async with self.session_maker() as session:
            try:
                yield session
                await session.commit()
            except Exception as e:
                await session.rollback()
                logger.exception("Error in session: %s", e)
                raise

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

    async def _exist_entry_by_field(self, session: AsyncSession, field: str, value: Any) -> bool:
        logger.info(f"Checking if {self.model.__name__} with {field}={value} exists")
        stmt = select(self.model).where(getattr(self.model, field) == value)
        result = await session.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def _get_one_entry(self, session: AsyncSession, **filters: dict) -> ModelType:
        stmt = select(self.model).filter_by(**filters)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    @_auto_session
    async def create(self, *, data: CreateSchemaType, **kwargs) -> ModelType:
        session = kwargs["session"]
        instance = self.model(**data.model_dump())
        return await self._create_one_entry(session=session, instance=instance)

    @_auto_session
    async def exist(self, *, field: str, value: Any, **kwargs) -> bool:
        session = kwargs["session"]
        return await self._exist_entry_by_field(session=session, field=field, value=value)

    @_auto_session
    async def get(self, **kwargs) -> ModelType:
        session = kwargs["session"]
        filters = {k: v for k, v in kwargs.items() if k != "session"}
        return await self._get_one_entry(session=session, **filters)
