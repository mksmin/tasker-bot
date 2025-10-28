from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from crud.managers import BaseCRUDManager
from database import Task


class AffirmationManager(BaseCRUDManager[Task]):
    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        super().__init__(
            session=session,
            model=Task,
        )

    async def create_affirmation(self) -> Task:
        pass

    async def get_affirmations_by_id(
        self,
        affirm_id: int,
    ) -> Task:
        pass

    async def get_random_affirmation(
        self,
        user_id: int,
        count: int = 5,
    ) -> list[Task]:
        pass

    async def get_paginated_affirmations(
        self,
        user_id: int,
        offset: int,
        limit: int,
    ) -> list[Task]:
        pass

    async def remove_affirmation(
        self,
        user_id: int,
        affirm_id: int,
    ) -> None | bool:
        stmt = select(Task).where(
            Task.id == affirm_id,
            Task.is_done.is_(False),
            Task.user_id == user_id,
        )
        result = await self.session.scalar(stmt)
        if result:
            result.is_done = True
            self.session.add(result)
            return True

        return None
