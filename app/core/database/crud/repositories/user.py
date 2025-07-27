# import libs
import logging

# import from libs
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from typing import Any

# import from project
from app.core.database.crud.repositories import BaseRepository
from database.models import User

# globals
log = logging.getLogger(__name__)


class UserRepository(BaseRepository[User]):
    ALLOWED_FIELDS = {
        "id",
        "user_tg",
        "username",
    }

    def __init__(
            self,
            session_maker: async_sessionmaker[AsyncSession],
    ):
        super().__init__(
            model=User,
            session_maker=session_maker,
        )

    async def create_user(
            self,
            *,
            session: AsyncSession,
            instance: User,
    ) -> User:
        log.info("Creating user with telegram id: %s", instance.user_tg)
        return await self.create(session=session, instance=instance)

    async def get_by_field(
            self,
            *,
            session: AsyncSession,
            field: str,
            value: Any,
    ):
        if field not in self.ALLOWED_FIELDS:
            raise ValueError(
                f"Field {field} is not allowed for search. Allowed fields are {self.ALLOWED_FIELDS}"
            )
        filters = {field: value}
        return await self.get_one_entry(session=session, **filters)
