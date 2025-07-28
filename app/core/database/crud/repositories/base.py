# import libs
import logging

# import from libs
from contextlib import asynccontextmanager
from functools import wraps
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from typing import TypeVar, ParamSpec, Generic, Callable, Concatenate, Coroutine, Any, Type, AsyncGenerator, Optional

# globals
ModelType = TypeVar("ModelType")
P = ParamSpec("P")
R = TypeVar("R")
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
logger = logging.getLogger(__name__)


class BaseRepository(Generic[ModelType]):
    def __init__(
            self,
            model: Type[ModelType],
    ):
        self.model = model

    async def create(self, session: AsyncSession, instance: ModelType) -> ModelType:
        session.add(instance)
        await session.flush()
        await session.refresh(instance)
        logger.debug("Created %s with id %d", self.model.__name__, instance.id)
        return instance

    async def is_exist(
            self,
            *,
            session: AsyncSession,
            field: str,
            value: Any
    ) -> bool:
        logger.debug("Checking if %s with %s=%s exists", self.model.__name__, field, value)
        if not hasattr(self.model, field):
            raise ValueError(f"Model {self.model.__name__} has no field {field}")

        stmt = select(self.model).where(getattr(self.model, field) == value)
        result = await session.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def get_one_entry(
            self,
            *,
            session: AsyncSession,
            **filters: dict[str, Any],
    ) -> ModelType:
        stmt = select(self.model).filter_by(**filters)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_paginated_entries(
            self,
            *,
            session: AsyncSession,
            offset: int = 0,
            limit: int = 5,
            filters: Optional[dict[str, Any]] = None,
            order_by: Optional[Any] = None,
    ):
        if offset < 0 or limit < 0:
            raise ValueError("Offset and limit must be non-negative")

        stmt = select(self.model)

        if filters:
            stmt = stmt.filter_by(**filters)

        if order_by is not None:
            stmt = stmt.order_by(order_by)

        stmt = stmt.offset(offset).limit(limit)
        result = await session.execute(stmt)
        return result.scalars().all()
