# import from libs

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from database.models import User
from database.schemas import UserReadSchema

from .base import BaseCRUDManager


class UserManager(BaseCRUDManager[User]):
    def __init__(
        self,
        session_maker: async_sessionmaker[AsyncSession],
    ) -> None:
        super().__init__(
            model=User,
            session_maker=session_maker,
        )

    async def get_user(
        self,
        *,
        id: int | None = None,
        user_tg: int | None = None,
    ) -> UserReadSchema:
        """
        Получить пользователя по id или Telegram ID (user_tg).
        Один из параметров обязательно должен быть передан

        raises:
            ValueError: если параметры не переданы или пользователь не найден
        """

        if id is None and user_tg is None:
            msg_error = "Either 'id' or 'user_tg' must be provided"
            raise ValueError(msg_error)

        filters = {}
        if id is not None:
            filters["id"] = id
        if user_tg is not None:
            filters["user_tg"] = user_tg

        user_model = await self.get(**filters)

        if user_model is None:
            msg_error = "User not found"
            raise ValueError(msg_error)

        return UserReadSchema.model_validate(user_model)
