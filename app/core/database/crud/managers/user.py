import logging

from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated, TYPE_CHECKING, TypeVar

from app.core.database.crud.managers import auto_session
from app.core.database.schemas import UserCreateSchema, UserReadSchema

if TYPE_CHECKING:
    from app.core.database.crud.repositories import BaseRepository, UserRepository

# globals
log = logging.getLogger(__name__)
ModelType = TypeVar("ModelType", bound="BaseRepository")


class UserManager:
    def __init__(self, repo: "UserRepository"):
        self.repo = repo

    @auto_session
    async def create_user(
            self,
            user_data: Annotated[dict, UserCreateSchema],
            *,
            session: AsyncSession,
    ) -> UserReadSchema:
        try:
            instance = UserCreateSchema(**user_data)
            filtered = {
                "field": "user_tg",
                "value": instance.user_tg
            }
            exist = await self.repo.is_exist(
                session=session,
                **filtered
            )
            if exist:
                user = await self.repo.get_by_field(
                    session=session,
                    **filtered
                )
                return UserReadSchema.model_validate(user)

            user = await self.repo.create_user(
                session=session,
                data=instance.model_dump()
            )
            return UserReadSchema.model_validate(user)

        except Exception as e:
            log.error(
                "Failed to create user", exc_info=True
            )
            raise e
