# import from libs
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

# import from modules
from .base import BaseCRUDManager
from database.models import User
from database.schemas import UserCreateSchema


class UserManager(BaseCRUDManager[User]):

    def __init__(self, session_maker: async_sessionmaker[AsyncSession]):
        super().__init__(
            model=User,
            session_maker=session_maker,
        )

    async def create_user(self, user_data: dict):
        instance = UserCreateSchema(**user_data)
        exist = await self.exist(field="user_tg", value=instance.user_tg)
        if exist:
            return await self.get(user_tg=instance.user_tg)

        return await super().create(data=instance)
