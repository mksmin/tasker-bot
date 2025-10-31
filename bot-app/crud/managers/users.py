from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from crud.managers import BaseCRUDManager
from database import User, UserSettings
from schemas.users import UserCreateSchema, UserSettingsUpdateSchema


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
        await self.session.flush()
        return instance

    async def get_all_users(self) -> Sequence[User]:
        stmt = select(User).order_by(User.id)
        query = await self.session.execute(stmt)
        return query.scalars().all()

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
    ) -> User | None:
        return await super().get(obj_id=user_id)

    async def get_or_create_user_settings(
        self,
        user: User,
    ) -> UserSettings:
        settings = (
            await self.session.execute(
                select(UserSettings)
                .where(UserSettings.user_id == user.id)
                .options(
                    selectinload(
                        UserSettings.user,
                    ),
                ),
            )
        ).scalar_one_or_none()

        if settings is None:
            settings = UserSettings(user_id=user.id)
            self.session.add(settings)
            await self.session.flush()

        return settings

    async def update_user_settings(
        self,
        settings: UserSettings,
        settings_in: UserSettingsUpdateSchema,
    ) -> UserSettings:
        for field_name, value in settings_in:
            setattr(settings, field_name, value)
        self.session.add(settings)
        return settings
