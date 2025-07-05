# import from libs
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

# import from modules
from .base import BaseCRUDManager
from .user import UserManager
from database.models import Task
from database.schemas import UserCreateSchema, TaskCreateSchema, UserReadSchema


class TaskManager(BaseCRUDManager[Task]):
    def __init__(self, session_maker: async_sessionmaker[AsyncSession]):
        super().__init__(
            model=Task,
            session_maker=session_maker,
        )
        self.user_manager = None

    def set_user_manager(self, manager: "UserManager"):
        self.user_manager = manager

    async def create_task(self, user_tg: int, task_text: str):
        user = await self.user_manager.get(user_tg=user_tg)
        user_schema = UserReadSchema.model_validate(user)
        print(f'user_schema: {user_schema}')
        # return await user_schema
        task_schema = TaskCreateSchema(
            text_task=task_text,
            user_id=user_schema.id
        )

        return await self.create(data=task_schema)
