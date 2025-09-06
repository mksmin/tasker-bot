# import from libs
from typing import Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

# import from modules
from .base import BaseCRUDManager
from .user import UserManager
from database.models import Task
from database.schemas import TaskCreateSchema, TaskReadSchema, UserReadSchema


class TaskManager(BaseCRUDManager[Task]):
    def __init__(self, session_maker: async_sessionmaker[AsyncSession]) -> None:
        super().__init__(
            model=Task,
            session_maker=session_maker,
        )
        self.user_manager: Optional["UserManager"] = None

    def set_user_manager(self, manager: "UserManager") -> None:
        self.user_manager = manager

    async def create_task(
        self,
        user_tg: int,
        task_text: str,
    ) -> TaskReadSchema:
        assert self.user_manager is not None, "UserManager is not set"
        user = await self.user_manager.get_user(user_tg=user_tg)

        task_schema = TaskCreateSchema(
            text_task=task_text,
            user_id=user.id,
        )
        created_model = await self.create(data=task_schema)
        return TaskReadSchema.model_validate(created_model)

    async def get_task_by_id(self, task_id: int) -> TaskReadSchema:
        result = await self.get(id=task_id)
        return TaskReadSchema.model_validate(result)

    async def get_random_tasks(
        self,
        user_tg: int,
        count: int = 5,
    ) -> list[TaskReadSchema]:
        assert self.user_manager is not None, "UserManager is not set"
        user = await self.user_manager.get_user(user_tg=user_tg)
        async with self.get_session() as session:
            stmt = (
                select(Task)
                .where(Task.user_id == user.id, Task.is_done.is_(False))
                .order_by(func.random())
                .limit(count)
            )
            result = await session.execute(stmt)
            tasks = result.scalars().all()

            if not tasks:
                return []

            return [TaskReadSchema.model_validate(task) for task in tasks]

    async def get_paginated_tasks(
        self,
        user_tg: int,
        offset: int,
        limit: int,
    ) -> list[TaskReadSchema]:
        assert self.user_manager is not None, "UserManager is not set"
        user = await self.user_manager.get_user(user_tg=user_tg)

        tasks = await self.get_all(
            offset=offset,
            limit=limit,
            filters={"user_id": user.id},
            order_by=Task.id.desc(),
        )

        if not tasks:
            return []

        return [TaskReadSchema.model_validate(task) for task in tasks]

    async def mark_as_done(self, task_id: int) -> bool:
        async with self.get_session() as session:
            stmt = select(Task).where(Task.id == task_id, Task.is_done.is_(False))
            result = await session.scalar(stmt)

            if not result:
                return False

            if not result.is_done:
                result.is_done = True
                await session.commit()
                return True
            return False
