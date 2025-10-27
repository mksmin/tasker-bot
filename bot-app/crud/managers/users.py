from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from crud.managers import BaseCRUDManager
from database import User, UserSettings
from schemas.users import UserCreateSchema


class UserManager(BaseCRUDManager[User]):
    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        super().__init__(
            session=session,
            model=User,
        )

    async def create_user(
        self,
        user_data: UserCreateSchema,
    ) -> User:
        instance = User(**user_data.model_dump())
        self.session.add(instance)
        return instance

    async def get_user_by_tg_id(
        self,
        tg_id: int,
    ) -> User | None:
        stmt = select(User).where(User.user_tg == tg_id)
        query = await self.session.execute(stmt)
        return query.scalar_one_or_none()

    async def get_user_by_id(
        self,
        user_id: int,
    ) -> User:
        return await super().get(obj_id=user_id)

    async def get_user_with_settings(
        self,
        user_tg: int,
    ) -> UserSettings | None:
        stmt = select(UserSettings).options(
            joinedload(UserSettings.user),
        )
        filtered_stmt = stmt.where(
            UserSettings.user.user_tg == user_tg,
        )
        query = await self.session.execute(filtered_stmt)
        return query.scalar_one_or_none()
