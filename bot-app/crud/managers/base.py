import logging
from typing import Generic, TypeVar

from sqlalchemy.ext.asyncio import AsyncSession

from database import Base

log = logging.getLogger(__name__)
ModelType = TypeVar("ModelType", bound=Base)


class BaseCRUDManager(Generic[ModelType]):
    def __init__(
        self,
        session: AsyncSession,
        model: type[ModelType],
    ) -> None:
        self.session = session
        self.model = model

    async def get(
        self,
        obj_id: int,
    ) -> ModelType | None:
        return await self.session.get(self.model, obj_id)

    def add(
        self,
        obj: ModelType,
    ) -> ModelType:
        self.session.add(obj)
        return obj

    async def remove(
        self,
        obj_id: int,
    ) -> None:
        pass
